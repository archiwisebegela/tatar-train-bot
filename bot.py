import datetime as dt
import json
import logging
import os
from pathlib import Path
import sqlite3
import time
import urllib.request
import urllib.error
from course import UNITS, lesson
from grammar import PAGES

ROOT = Path(__file__).resolve().parent
# Read local settings without requiring external libraries.
if (ROOT / '.env').exists():
    for line in (ROOT / '.env').read_text(encoding='utf-8-sig').splitlines():
        key, sep, value = line.partition('=')
        if sep and key.strip() in ('TELEGRAM_BOT_TOKEN', 'UTC_OFFSET'):
            os.environ.setdefault(key.strip(), value.strip().strip('\"').strip("'"))
# Fixed UTC+3 avoids dependence on Windows timezone databases.
TZ = dt.timezone(dt.timedelta(hours=int(os.getenv('UTC_OFFSET', '3'))))

class Store:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, joined TEXT, level INTEGER DEFAULT 0,
          paused INTEGER DEFAULT 0, reminded TEXT);
        CREATE TABLE IF NOT EXISTS days(user INTEGER, day TEXT, level INTEGER, questions TEXT,
          position INTEGER DEFAULT 0, correct INTEGER DEFAULT 0, PRIMARY KEY(user,day));
        CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value INTEGER);
        ''')
    def user(self, uid, today):
        self.db.execute('INSERT OR IGNORE INTO users(id,joined) VALUES(?,?)', (uid, today))
        self.db.commit()
        return self.db.execute('SELECT * FROM users WHERE id=?', (uid,)).fetchone()
    def day(self, uid, today):
        user = self.user(uid, today)
        self.db.execute('INSERT OR IGNORE INTO days(user,day,level,questions) VALUES(?,?,?,?)',
                        (uid,today,user['level'],json.dumps(lesson(user['level'],f'{uid}:{today}'),ensure_ascii=False)))
        self.db.commit()
        return self.db.execute('SELECT * FROM days WHERE user=? AND day=?',(uid,today)).fetchone()
    def answer(self, uid, today, position, choice):
        row = self.day(uid,today)
        if row['position'] != position or position >= 20:
            return None
        q = json.loads(row['questions'])[position]
        if choice not in range(len(q['choices'])):
            return None
        ok = choice == q['correct']
        score = row['correct'] + int(ok)
        self.db.execute('UPDATE days SET position=position+1,correct=? WHERE user=? AND day=?',
                        (score,uid,today))
        if position == 19 and score >= 16:
            self.db.execute('UPDATE users SET level=? WHERE id=?',(min(row['level']+1,len(UNITS)-1),uid))
        self.db.commit()
        return ok,q
    def due(self, now):
        today = now.date().isoformat()
        yesterday = (now.date()-dt.timedelta(days=1)).isoformat()
        if now.hour < 19:
            return []
        return self.db.execute('''SELECT u.id FROM users u
          LEFT JOIN days d ON d.user=u.id AND d.day=?
          LEFT JOIN days t ON t.user=u.id AND t.day=?
          WHERE u.joined<=? AND u.paused=0 AND (u.reminded IS NULL OR u.reminded<>?)
          AND COALESCE(d.position,0)<20 AND COALESCE(t.position,0)<20''',
          (yesterday,today,yesterday,today)).fetchall()

class Telegram:
    def __init__(self, token):
        self.base = 'https://api.telegram.org/bot'+token+'/'
    def call(self, method, **data):
        req = urllib.request.Request(self.base+method,json.dumps(data).encode(),
                                     {'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req,timeout=40) as response:
                result = json.load(response)
        except urllib.error.HTTPError as exc:
            # Never print exception URLs: they contain the token.
            raise RuntimeError(f'Telegram HTTP {exc.code}') from None
        except urllib.error.URLError:
            raise RuntimeError('Telegram connection failed') from None
        if not result.get('ok'):
            raise RuntimeError('Telegram request failed')
        return result['result']

def keyboard(rows):
    return {'inline_keyboard':[[{'text':text,'callback_data':data} for text,data in row] for row in rows]}

class Bot:
    def __init__(self, store, api):
        self.store,self.api = store,api
    def send(self, uid, text, markup=None):
        data = dict(chat_id=uid,text=text)
        if markup:
            data['reply_markup']=markup
        self.api.call('sendMessage',**data)
    def menu(self, uid):
        self.send(uid,'Главное меню',keyboard([
            [('📚 Задания на сегодня','/learn')],
            [('📖 Грамматика','/grammar'),('📊 Прогресс','/progress')],
            [('🔕 Без напоминаний','/pause'),('🔔 Напоминать','/resume')]]))
    def grammar(self, uid, page=None):
        if page is None:
            rows=[[(title,f'g:{i}')] for i,(title,_) in enumerate(PAGES)]
            rows.append([('🏠 Главное меню','/menu')])
            self.send(uid,'📖 Основы татарской грамматики\nВыберите тему:',keyboard(rows))
        else:
            title,body=PAGES[page]
            nav=[]
            if page>0: nav.append(('← Назад',f'g:{page-1}'))
            if page<len(PAGES)-1: nav.append(('Дальше →',f'g:{page+1}'))
            self.send(uid,f'📖 {title}\n\n{body}',keyboard([nav,
                [('Все темы','/grammar'),('🏠 Меню','/menu')]]))
    def show(self, uid, today):
        row = self.store.day(uid,today)
        if row['position'] == 20:
            message = f"✅ Норма выполнена: 20/20. Верных ответов: {row['correct']}/20."
            if row['correct'] < 16:
                message += '\nЗавтра закрепим эту тему: для перехода нужно 16 верных ответов.'
            elif row['level'] == len(UNITS)-1:
                message += '\nНачальный курс завершён! Следующие дни — закрепление последней темы.'
            else:
                message += '\nЗавтра откроется следующая тема!'
            return self.send(uid,message)
        q = json.loads(row['questions'])[row['position']]
        text = f"📚 {UNITS[row['level']][0]} · {row['position']+1}/20\n\n{q['prompt']}"
        if row['position'] == 0:
            text = UNITS[row['level']][1]+'\n\n'+text
        buttons = [[(label,f"a:{today}:{row['position']}:{i}")] for i,label in enumerate(q['choices'])]
        buttons.append([('📖 Грамматика','/grammar'),('🏠 Меню','/menu')])
        self.send(uid,text,keyboard(buttons))
    def handle(self, update, now):
        today = now.date().isoformat()
        cb = update.get('callback_query')
        msg = cb.get('message') if cb else update.get('message')
        if not msg or msg['chat']['type'] != 'private':
            return
        uid = msg['chat']['id']
        if cb and cb['from']['id'] != uid:
            return
        self.store.user(uid,today)
        action = cb.get('data','') if cb else msg.get('text','').split('@')[0].strip()
        if cb:
            self.api.call('answerCallbackQuery',callback_query_id=cb['id'])
        if action.startswith('a:'):
            try:
                _,day,pos,choice=action.split(':')
                result = self.store.answer(uid,today,int(pos),int(choice)) if day==today else None
            except (ValueError,IndexError):
                result = None
            if result:
                ok,q=result
                self.send(uid,('✅ Верно! ' if ok else '❌ Правильный ответ: ')+q['explanation'],
                          keyboard([[('Дальше →','/learn')]]))
            else:
                self.send(uid,'Этот ответ уже принят или задание устарело.',keyboard([[('Продолжить','/learn')]]))
        elif action=='/menu':
            self.menu(uid)
        elif action=='/grammar':
            self.grammar(uid)
        elif action.startswith('g:'):
            try:
                page=int(action[2:])
            except ValueError:
                page=-1
            self.grammar(uid,page if 0<=page<len(PAGES) else None)
        elif action in ('/learn','/start'):
            if action=='/start':
                self.send(uid,'Исәнмесез! Учим татарский с нуля: 20 заданий каждый день.\n'
                          'После пропущенной нормы напомню в 19:00 (UTC+3 по умолчанию).\n'
                          '/progress — прогресс · /pause — выключить напоминания · /resume — включить')
            if action=='/start':
                self.menu(uid)
            else:
                self.show(uid,today)
        elif action in ('/pause','/resume'):
            self.store.db.execute('UPDATE users SET paused=? WHERE id=?',(int(action=='/pause'),uid))
            self.store.db.commit()
            self.send(uid,'Напоминания выключены.' if action=='/pause' else 'Напоминания включены.')
        elif action=='/progress':
            row=self.store.day(uid,today)
            completed=self.store.db.execute('SELECT COUNT(*) FROM days WHERE user=? AND position=20',(uid,)).fetchone()[0]
            self.send(uid,f"Сегодня: {row['position']}/20. Верно: {row['correct']}.\n"
                      f"Тема: {UNITS[row['level']][0]}. Завершено дней: {completed}.",
                      keyboard([[('Продолжить','/learn')]]))
        else:
            self.menu(uid)
    def remind(self, now):
        for row in self.store.due(now):
            try:
                self.send(row['id'],'Вчера дневная норма не была выполнена. Вернёмся к татарскому? Сегодня — 20 заданий.',
                          keyboard([[('Начать урок','/learn')]]))
            except RuntimeError as exc:
                if str(exc)=='Telegram HTTP 403':
                    self.store.db.execute('UPDATE users SET paused=1 WHERE id=?',(row['id'],))
                    self.store.db.commit()
                continue
            self.store.db.execute('UPDATE users SET reminded=? WHERE id=?',(now.date().isoformat(),row['id']))
            self.store.db.commit()

def main():
    token=os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise SystemExit('Set TELEGRAM_BOT_TOKEN before starting. See README.md.')
    store=Store(ROOT/'progress.sqlite3')
    bot=Bot(store,Telegram(token))
    saved=store.db.execute("SELECT value FROM meta WHERE key='offset'").fetchone()
    offset=saved[0] if saved else 0
    logging.basicConfig(level=logging.INFO)
    while True:
        try:
            bot.remind(dt.datetime.now(TZ))
            updates=bot.api.call('getUpdates',offset=offset,timeout=20,allowed_updates=['message','callback_query'])
            for update in updates:
                bot.handle(update,dt.datetime.now(TZ))
                offset=update['update_id']+1
                store.db.execute("INSERT OR REPLACE INTO meta VALUES('offset',?)",(offset,))
                store.db.commit()
        except (RuntimeError,TimeoutError,OSError):
            logging.warning('Connection interrupted; retrying in 5 seconds.')
            time.sleep(5)

if __name__=='__main__':
    main()

import datetime as dt
import unittest
from bot import Store, Bot, TZ
from course import lesson, UNITS

class FakeAPI:
    def __init__(self): self.calls=[]
    def call(self, method, **data): self.calls.append((method,data))

class Tests(unittest.TestCase):
    def test_language_selection_keeps_progress_and_tatar(self):
        from i18n import translate,GRAMMAR_EN
        from grammar import PAGES
        s=Store(':memory:');api=FakeAPI();b=Bot(s,api)
        now=dt.datetime(2026,10,14,tzinfo=TZ)
        def act(text):
            b.handle({'message':{'chat':{'id':1,'type':'private'},'text':text}},now)
        act('/learn');before=s.day(1,'2026-10-14')['position']
        act('lang:en')
        self.assertEqual(s.language(1),'en')
        self.assertEqual(api.calls[-1][1]['text'],'Main menu')
        self.assertEqual(s.day(1,'2026-10-14')['position'],before)
        act('/learn')
        self.assertIn('Choose the translation:',api.calls[-1][1]['text'])
        self.assertEqual(translate('Мин язам.','en'),'Мин язам.')
        self.assertEqual(translate('Выберите перевод: Я пишу.','en'),'Choose the translation: I am writing.')
        self.assertEqual(len(GRAMMAR_EN),len(PAGES))
        for i in range(len(PAGES)):
            act(f'g:{i}')
            self.assertIn(GRAMMAR_EN[i][0],api.calls[-1][1]['text'])
        act('lang:ru');self.assertEqual(api.calls[-1][1]['text'],'Главное меню')
    def test_unlimited_practice_keeps_daily_progress(self):
        import json
        s=Store(':memory:');today='2026-10-14'
        self.assertIsNone(s.practice(1,today))
        for i,q in enumerate(json.loads(s.day(1,today)['questions'])):
            s.answer(1,today,i,q['correct'])
        level=s.user(1,today)['level']
        ids=[]
        for block in range(3):
            row=s.practice(1,today);ids.append(row['id'])
            self.assertEqual(s.practice(1,today)['id'],row['id'])
            questions=json.loads(row['questions'])
            for i,q in enumerate(questions):
                self.assertIsNone(s.practice_answer(2,today,row['id'],i,q['correct']))
                self.assertIsNone(s.practice_answer(1,'2026-10-15',row['id'],i,q['correct']))
                self.assertIsNotNone(s.practice_answer(1,today,row['id'],i,q['correct']))
                self.assertIsNone(s.practice_answer(1,today,row['id'],i,q['correct']))
        self.assertEqual(len(set(ids)),3)
        self.assertEqual(s.day(1,today)['position'],20)
        self.assertEqual(s.user(1,today)['level'],min(level+3,len(UNITS)-1))
        self.assertEqual([r[0] for r in s.db.execute('SELECT level FROM practice ORDER BY id')],[1,2,3])
        self.assertEqual(s.db.execute('SELECT SUM(position) FROM practice').fetchone()[0],60)
    def test_practice_end_offers_another_block(self):
        import json
        s=Store(':memory:');api=FakeAPI();b=Bot(s,api);today='2026-10-14'
        s.day(1,today);s.db.execute('UPDATE days SET position=20');s.db.commit()
        row=s.practice(1,today);questions=json.loads(row['questions'])
        for i,q in enumerate(questions):
            b.handle({'callback_query':{'id':str(i),'from':{'id':1},
                'data':f"p:{row['id']}:{i}:{q['correct']}",'message':{'chat':{'id':1,'type':'private'}}}},
                dt.datetime(2026,10,14,tzinfo=TZ))
        self.assertIn('Блок практики завершён',api.calls[-1][1]['text'])
        self.assertEqual(api.calls[-1][1]['reply_markup']['inline_keyboard'][0][0]['callback_data'],'/practice')
    def test_persistent_store_migrates_legacy_once(self):
        import uuid
        from pathlib import Path
        from unittest.mock import patch
        import bot
        root=Path(__file__).resolve().parent/('test-data-'+uuid.uuid4().hex)
        root.mkdir()
        try:
            old=Store(root/'progress.sqlite3')
            old.user(42,'2026-10-13')
            old.db.close()
            with patch.object(bot,'ROOT',root),patch.dict(bot.os.environ,{'DATA_DIR':str(root/'data')}):
                new=bot.open_store()
                self.assertEqual(new.db.execute('SELECT COUNT(*) FROM users').fetchone()[0],1)
                new.user(43,'2026-10-14');new.db.close()
                reopened=bot.open_store()
                self.assertEqual(reopened.db.execute('SELECT COUNT(*) FROM users').fetchone()[0],2)
                reopened.db.close()
        finally:
            for file in (root/'progress.sqlite3',root/'data'/'progress.sqlite3'):
                if file.exists(): file.unlink()
            if (root/'data').exists(): (root/'data').rmdir()
            root.rmdir()
    def test_grammar_navigation_preserves_progress(self):
        from grammar import PAGES
        s=Store(':memory:'); api=FakeAPI(); b=Bot(s,api)
        now=dt.datetime(2026,10,13,tzinfo=TZ)
        s.day(1,'2026-10-13')
        for action in ['/start','/grammar']+[f'g:{i}' for i in range(len(PAGES))]+['g:999','g:bad','/menu']:
            b.handle({'message':{'chat':{'id':1,'type':'private'},'text':action}},now)
        self.assertEqual(s.day(1,'2026-10-13')['position'],0)
        for method,data in api.calls:
            if method=='sendMessage':
                self.assertLess(len(data['text']),4096)
                for row in data.get('reply_markup',{}).get('inline_keyboard',[]):
                    for button in row:
                        self.assertLessEqual(len(button['callback_data'].encode()),64)
    def test_content(self):
        for level in range(len(UNITS)):
            questions=lesson(level,'test')
            self.assertEqual(len(questions),20)
            for q in questions:
                self.assertEqual(len(set(q['choices'])),4)
                self.assertIn(q['correct'],range(4))
    def test_completion_and_duplicate(self):
        s=Store(':memory:'); day='2026-10-13'
        questions=__import__('json').loads(s.day(1,day)['questions'])
        for i,q in enumerate(questions):
            self.assertIsNotNone(s.answer(1,day,i,q['correct']))
            self.assertIsNone(s.answer(1,day,i,q['correct']))
        self.assertEqual(s.day(1,day)['position'],20)
        self.assertEqual(s.user(1,day)['level'],1)
        self.assertEqual(s.day(1,'2026-10-14')['level'],1)
    def test_failure_keeps_level(self):
        s=Store(':memory:'); day='2026-10-13'
        questions=__import__('json').loads(s.day(1,day)['questions'])
        for i,q in enumerate(questions): s.answer(1,day,i,(q['correct']+1)%4)
        self.assertEqual(s.user(1,day)['level'],0)
    def test_reminder_once_and_pause(self):
        s=Store(':memory:'); s.user(1,'2026-10-12')
        api=FakeAPI(); b=Bot(s,api)
        self.assertEqual(s.due(dt.datetime(2026,10,13,18,tzinfo=TZ)),[])
        now=dt.datetime(2026,10,13,19,tzinfo=TZ)
        b.remind(now); b.remind(now)
        self.assertEqual(len(api.calls),1)
        s.db.execute('UPDATE users SET paused=1'); s.db.commit()
        self.assertEqual(s.due(now+dt.timedelta(days=1)),[])
    def test_completed_yesterday_no_reminder(self):
        s=Store(':memory:'); s.day(1,'2026-10-12')
        s.db.execute('UPDATE days SET position=20'); s.db.commit()
        self.assertEqual(s.due(dt.datetime(2026,10,13,19,tzinfo=TZ)),[])
    def test_stale_callback(self):
        s=Store(':memory:'); api=FakeAPI(); b=Bot(s,api)
        b.handle({'callback_query':{'id':'1','from':{'id':1},'data':'a:2026-10-12:0:0',
                  'message':{'chat':{'id':1,'type':'private'}}}},dt.datetime(2026,10,13,tzinfo=TZ))
        self.assertEqual(s.day(1,'2026-10-13')['position'],0)

if __name__=='__main__': unittest.main()

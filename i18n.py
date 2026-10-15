import re
from course import UNITS

UI = {
 'Главное меню':'Main menu', 'Задания на сегодня':'Daily lesson',
 'Практиковать дальше':'Keep practising', 'Грамматика':'Grammar', 'Прогресс':'Progress',
 'Без напоминаний':'Mute reminders', 'Напоминать':'Enable reminders', 'Меню':'Menu',
 'Основы татарской грамматики':'Tatar grammar basics', 'Выберите тему:':'Choose a topic:',
 'Назад':'Back', 'Дальше':'Next', 'Все темы':'All topics', 'ещё 20':'20 more',
 'Норма выполнена:':'Daily goal complete:', 'Верных ответов:':'Correct answers:',
 'Продолжите практику, чтобы закрепить тему: для перехода нужно 16 верных ответов.':
 'Keep practising this topic. You need 16 correct answers to advance.',
 'Начальный курс завершён! Можно закреплять последнюю тему.':
 'Starter course complete! You can keep reviewing the final topic.',
 'Следующая тема уже открыта — нажмите «Практиковать дальше»!':
 'The next topic is unlocked — tap “Keep practising”!',
 'Сначала выполните дневную норму — 20 заданий.':'Complete your daily goal of 20 questions first.',
 'Продолжить норму':'Continue daily lesson', 'Дополнительная практика':'Extra practice',
 'Задание ':'Question ', 'Выберите перевод:':'Choose the translation:',
 'Этот ответ уже принят или задание устарело.':'This answer was already accepted or the question has expired.',
 'Продолжить практику':'Continue practice', 'Верно!':'Correct!', 'Правильный ответ:':'Correct answer:',
 'Блок практики завершён:':'Practice block complete:', 'верных.':'correct.',
 'Можно пройти ещё 20 — сколько угодно раз!':'You can do another 20, as many times as you like!',
 'Следующая тема открыта!':'Next topic unlocked!',
 'Следующий блок закрепит эту тему. Для перехода нужно 16 верных ответов.':
 'The next block reviews this topic. You need 16 correct answers to advance.',
 'Продолжить':'Continue', 'Исәнмесез! Учим татарский с нуля: 20 заданий каждый день.':
 'Welcome! Learn Tatar from scratch: 20 questions every day.',
 'После пропущенной нормы напомню в 19:00 (UTC+3 по умолчанию).':
 'After a missed daily goal, I remind you at 19:00 (UTC+3 by default).',
 'прогресс':'progress', 'выключить напоминания':'mute reminders', 'включить':'enable',
 'Напоминания выключены.':'Reminders disabled.', 'Напоминания включены.':'Reminders enabled.',
 'Сегодня:':'Today:', 'Верно:':'Correct:', 'Тема:':'Topic:', 'Завершено дней:':'Completed days:',
 'Дополнительная практика сегодня:':'Extra practice today:', 'заданий,':'questions,',
 'Вчера дневная норма не была выполнена. Вернёмся к татарскому? Сегодня — 20 заданий.':
 'Yesterday’s daily goal was not completed. Ready for some Tatar? Today’s goal is 20 questions.',
 'Начать урок':'Start lesson', 'Язык бота':'Bot language',
 'Выберите язык бота / Choose the bot language:':'Выберите язык бота / Choose the bot language:',
 'Язык сохранён.':'Language saved.',
 'Открытая тема:':'Unlocked topic:',
 'Это последняя тема начального курса. Дальше доступно её повторение.':
 'This is the final topic of the starter course. You can continue reviewing it.',
}
UNIT_EN = [
 ('Greetings','Learn greetings and polite expressions.'),
 ('People and family','Мин means I, син means you, ул means he or she.'),
 ('Numbers','Learn the numbers from one to ten.'),
 ('Food and home','Words for everyday life.'),
 ('First sentences','Мин means I; -м marks the first-person singular in these verbs.'),
    ('My, your, our','Possession uses suffixes: өй means house; өем means my house.'),
    ('Where, where to, where from','Direction: -га/-гә/-ка/-кә. Location: -да/-дә/-та/-тә. Origin: -дан/-дән/-тан/-тән.'),
    ('Negation and existence','бармыйм means I do not go. Юк means there is no; түгел negates a noun predicate.'),
    ('What happened yesterday','Definite past: -ды/-де or -ты/-те followed by a personal ending.'),
    ('Conversation questions','Yes/no questions use -мы/-ме. Кайда means where; кайчан means when; нәрсә means what.'),
]
VOCAB_EN = [
 ['Hi','Hello (formal)','Thank you','Please (request)','Bye','Goodbye','Yes','No','Good morning','Good evening'],
 ['I','you (singular)','he / she','we','you (plural / formal)','they','mother','father','child','family'],
 ['one','two','three','four','five','six','seven','eight','nine','ten'],
 ['water','tea','milk','bread','apple','soup','house','door','window','book'],
 ['I am reading.','I am writing.','I am working.','I am learning Tatar.','I am drinking water.',
  'I am at home.','This is a book.','This is my mother.','What is your name?','My name is Alsu.'],
 ['my book','your book (singular)','his / her book','our book','your book (plural / formal)',
  'my house','your house (singular)','his / her house','our house','your house (plural / formal)'],
 ['I go to school.','I study at school.','I return from school.','I return home.','I read at home.',
  'I go to the shop.','I work at the shop.','The book is on the table.','I live in Kazan.','I go to the city.'],
 ['I am not going.','I am not coming.','I am not working.','I am not reading.','I am not writing.',
  'I am not drinking water.','This is not a book.','I am not a teacher.','I have a book.','I do not have a book.'],
 ['I went.','I came.','I returned.','I read (past).','I wrote.','I worked.','I drank water.',
  'We went.','You came.','They returned.'],
 ['Are you going?','Are you coming?','Are you working?','Are you reading?','Do you speak Tatar?',
  'Where do you live?','Where do you work?','When will you come?','What is this?','Who is this?'],
]
# Whole Russian phrases are replaced once; translated text is never translated again.
for unit, translated, vocabulary in zip(UNITS, UNIT_EN, VOCAB_EN):
    UI.update(zip(unit[:2],translated))
    UI.update((pair[1],meaning) for pair,meaning in zip(unit[2],vocabulary))
_PATTERN = re.compile('|'.join(
    (r'(?<!\w)' if k[0].isalnum() else '')+re.escape(k)+
    (r'(?!\w)' if k[-1].isalnum() else '')
    for k in sorted(UI,key=len,reverse=True)))

def translate(text, language):
    if language!='en':
        return text
    # Single choices such as "я" must not match within another Russian word.
    if text in UI:
        return UI[text]
    return _PATTERN.sub(lambda match: UI[match.group()],text)

GRAMMAR_EN = [
 ('Sounds and suffixes', '''Tatar uses Cyrillic, including Ә, Ө, Ү, Җ, Ң, Һ.
Back vowels: а, ы, о, у. Front vowels: ә, э/е, ө, ү, и.
Suffixes usually follow vowel harmony: балалар (children), өйләр (houses).
Loanwords may be exceptions. Voiceless consonants often take к/т instead of г/д:
мәктәпкә (to school), шәһәргә (to the city).
Consonants may change: китап → китабым (my book).
Typical suffix order: stem → plural → possession → case.
өй-ләр-ебез-дә means in our houses. Tatar has no grammatical gender.'''),
 ('Six cases', '''1. Nominative — кем? нәрсә? Who? What? No suffix: китап (book).
2. Genitive — кемнең? нәрсәнең? Whose? -ның/-нең: китапның.
3. Dative — кемгә? нәрсәгә? кая? To whom/where? -га/-гә/-ка/-кә: китапка.
4. Accusative — кемне? нәрсәне? Definite direct object. -ны/-не: китапны.
5. Ablative — кемнән? нәрсәдән? кайдан? From whom/where? -дан/-дән/-тан/-тән/-нан/-нән: китаптан.
6. Locative-temporal — кемдә? нәрсәдә? кайда? Where/when? -да/-дә/-та/-тә: китапта.
Choose the suffix by the vowels and final consonant. After м, н, ң, ablative often uses -нан/-нән: урманнан (from the forest).
These are forms without possessive suffixes.'''),
 ('Declension: house and school', '''өй (house): өй / өйнең / өйгә / өйне / өйдән / өйдә.
мәктәп (school): мәктәп / мәктәпнең / мәктәпкә / мәктәпне / мәктәптән / мәктәптә.
The order is nominative, genitive, dative, accusative, ablative, locative.
Мин мәктәпкә барам. — I go to school.
Мин мәктәптә укыйм. — I study at school.
Мин мәктәптән кайтам. — I return from school.
Distinguish direction, location and the starting point.'''),
 ('Plural', '''Usually -лар/-ләр: бала → балалар (children), өй → өйләр (houses).
After м, н, ң: -нар/-нәр: урманнар (forests), көннәр (days).
After a number, the noun is normally singular: ике китап (two books).
Case follows the plural suffix: өйләргә (to the houses), балаларны (the children as a definite object).'''),
 ('Possession: my and your', '''минем өем — my house; синең өең — your house;
аның өе — his/her house; безнең өебез — our house;
сезнең өегез — your house (plural/formal); аларның өйләре — their house(s).
After consonants: -(ы)м/-(е)м, -(ы)ң/-(е)ң, -ы/-е, -ыбыз/-ебез, -ыгыз/-егез.
After vowels: -м, -ң, -сы/-се, -быз/-без, -гыз/-гез.
балам — my child; баласы — his/her child.
баланың китабы — the child’s book: the owner is genitive, the object has a possessive suffix.
Spelling after и/у/ү and consonant changes require care.'''),
 ('Cases with possession', '''My house: өем / өемнең / өемә / өемне / өемнән / өемдә.
His/her house: өе / өенең / өенә / өен / өеннән / өендә.
After first/second-person singular possession, dative uses -а/-ә.
After third-person possession: dative -на/-нә, accusative -н, locative -нда/-ндә, ablative -ннан/-ннән.
Мин аның өенә барам. — I go to his/her house.
Мин аның өендә. — I am at his/her house.'''),
 ('Pronouns and questions', '''мин — I; син — you; ул — he/she; без — we; сез — you (plural/formal); алар — they.
минем — my/of me; миңа — to me; мине — me; миннән — from me; миндә — at me.
синең — your; сиңа — to you; сине — you (object).
аның — his/her; аңа — to him/her; аны — him/her; аннан — from him/her; анда — there/at him/her.
кем? who; нәрсә? what; кайда? where; кая? where to; кайдан? where from;
кайчан? when; ничек? how; ничә? how many; ни өчен? why/what for.
бу — this; теге — that. Сез can address one person politely.'''),
 ('Present tense', '''барырга — to go; килергә — to come.
Present tense covers current and habitual actions.
барам / барасың / бара / барабыз / барасыз / баралар:
I go / you go / he or she goes / we go / you go / they go.
киләм / киләсең / килә / киләбез / киләсез / киләләр.
Vowel-final stems have forms such as укыйм (I read), эшлим (I work).
Мин көн саен татарча өйрәнәм. — I learn Tatar every day.
Personal endings allow pronouns to be omitted when the meaning is clear.'''),
 ('Negation and questions', '''Verb negation uses -ма/-мә before further suffixes.
Present negatives: бармыйм (I do not go), килмим (I do not come), укымыйм (I do not read).
бармыйсың / бармый / бармыйбыз / бармыйсыз / бармыйлар.
Question particle -мы/-ме is written together with the word:
Син барасыңмы? — Are you going? Сез киләсезме? — Are you coming?
түгел negates a noun predicate: Бу китап түгел. — This is not a book.
бар means there is; юк means there is not:
Минем китабым бар/юк. — I have/do not have a book.'''),
 ('Past and future', '''Definite past: -ды/-де, or -ты/-те after voiceless consonants.
бардым / бардың / барды / бардык / бардыгыз / бардылар.
килдем — I came; кайттым — I returned.
Мин кичә китап укыдым. — I read a book yesterday.
Past -ган/-гән/-кан/-кән can express a result or indirectly known information:
Ул килгән. — He/she has come (as it turns out).
Future -ачак/-әчәк, after vowels -ячак/-ячәк:
барачакмын — I will go; киләчәкмен — I will come; укыячакмын — I will read.
Future -ар/-әр/-ыр/-ер/-р: барырмын — I will probably go.
Choice depends on meaning and context.'''),
 ('Commands and conditions', '''бар! — go!; кил! — come!
барыгыз! / килегез! — plural or polite commands.
барма! / килмә! — do not go/come!
барыйк / килик — let us go/come.
Conditional -са/-сә with personal endings:
барсам — if I go; барсаң — if you go; барса — if he/she goes.
Килсәң, сөйләшербез. — If you come, we will talk.
Мин укый алам. — I can read. Мин укый алмыйм. — I cannot read.'''),
 ('Adjectives and numerals', '''Adjectives precede nouns and do not agree in number or case:
матур йорт — a beautiful house; матур йортлар — beautiful houses.
Comparative -рак/-рәк: матуррак (more beautiful), зуррак (bigger).
Superlative: иң матур — the most beautiful.
Ordinal suffixes -ынчы/-енче, after vowels -нчы/-нче:
беренче — first; икенче — second; алтынчы — sixth.
өч зур йорт — three big houses: normally no plural after a number.
The present copula is usually omitted: Бу йорт зур. — This house is big.'''),
 ('Word order and postpositions', '''Neutral order: subject → object → verb.
Мин китап укыйм. — I read a book.
Time and place often precede the verb: Мин бүген өйдә китап укыйм.
A definite object takes accusative: бу китапны укыйм (I read this book).
китап укыйм can mean reading a book/books in general.
Postpositions follow nouns: дустым белән (with my friend), синең өчен (for you),
өйгә кадәр (up to the house), дәрестән соң (after class), дәрескә кадәр (before class).
һәм — and; ләкин — but; чөнки — because. Word order may change for emphasis.'''),
 ('Participles and converbs', '''Participles describe a noun through an action:
укый торган бала — a child who reads;
килгән кеше — a person who came; киләчәк кунак — a guest who will come.
Converbs link actions: -ып/-еп/-п, e.g. килеп (having come), укып (reading/having read).
Ул килеп утырды. — He/she came and sat down.
Verbal nouns -у/-ү: уку (reading/study), килү (coming).
Уку файдалы. — Reading is useful.
These forms are essential for complex sentences; translate the whole construction.'''),
 ('Word formation and voice', '''Common suffixes: -чы/-че (эшче — worker), -лы/-ле (балалы — having children),
-сыз/-сез (сусыз — without water), -лык/-лек (дуслык — friendship).
Voice changes participants: юу (wash) → юыну (wash oneself);
язу (write) → язылу (be written); уку (read) → укыту (teach).
Voice suffixes have several forms depending on the stem and meaning.
Learn derived verbs with examples. Analyse suffix chains from the stem outward.'''),
 ('Using this reference', '''Suggested order: sounds → plurals → cases → possession → pronouns → verbs → sentences.
This is a basic reference for literary Kazan Tatar; rare constructions and exceptions need further study.
Learn Tatar: https://www.learntatar.com/grammar
G. Burbiel’s grammar: https://ibtrussia.org/sites/default/files/files/TTR_Gram_R_web.pdf
Apertium morphology: https://wiki.apertium.org/wiki/Morphology_of_Tatar_language
Reading the reference does not count towards the daily 20 questions.'''),
]

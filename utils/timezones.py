# -*- coding: utf-8 -*-
import datetime
import pytz

locale_indexes = {'en' : 0,
                  'ru' : 1,
                  'ru-ru' : 1,
                  'en-us' : 0,
                  'en-gb' : 0}

known_timezones = {
    1 : [u'Europe/Moscow', u'Европа / Москва'],
    2 : [u'Africa/Abidjan', u'Африка / Абиджан'],
    3 : [u'Africa/Accra', u'Африка / Аккра'],
    4 : [u'Africa/Addis_Ababa', u'Африка / Аддис-Абеба'],
    5 : [u'Africa/Algiers', u'Африка / Алжир'],
    6 : [u'Africa/Asmara', u'Африка / Асмэра'],
    7 : [u'Africa/Bamako', u'Африка / Бамако'],
    8 : [u'Africa/Bangui', u'Африка / Банги'],
    9 : [u'Africa/Banjul', u'Африка / Банжул'],
    10 : [u'Africa/Bissau', u'Африка / Бисау'],
    11 : [u'Africa/Blantyre', u'Африка / Блантайр'],
    12 : [u'Africa/Brazzaville', u'Африка / Браззавиль'],
    13 : [u'Africa/Bujumbura', u'Африка / Бужумбура'],
    14 : [u'Africa/Cairo', u'Африка / Каир'],
    15 : [u'Africa/Casablanca', u'Африка / Касабланка'],
    16 : [u'Africa/Ceuta', u'Африка / Сеута'],
    17 : [u'Africa/Conakry', u'Африка / Конакри'],
    18 : [u'Africa/Dakar', u'Африка / Дакар'],
    19 : [u'Africa/Dar_es_Salaam', u'Африка / Дар-эс-Салам'],
    20 : [u'Africa/Djibouti', u'Африка / Джибути'],
    21 : [u'Africa/Douala', u'Африка / Дуала'],
    22 : [u'Africa/Freetown', u'Африка / Фритаун'],
    23 : [u'Africa/Gaborone', u'Африка / Габороне'],
    24 : [u'Africa/Harare', u'Африка / Хараре'],
    25 : [u'Africa/Johannesburg', u'Африка / Йоханнесбург'],
    26 : [u'Africa/Juba', u'Африка / Джуба'],
    27 : [u'Africa/Kampala', u'Африка / Кампала'],
    28 : [u'Africa/Khartoum', u'Африка / Хартум'],
    29 : [u'Africa/Kigali', u'Африка / Кигали'],
    30 : [u'Africa/Kinshasa', u'Африка / Киншаса'],
    31 : [u'Africa/Lagos', u'Африка / Лагос'],
    32 : [u'Africa/Libreville', u'Африка / Либревиль'],
    33 : [u'Africa/Lome', u'Африка / Ломе'],
    34 : [u'Africa/Luanda', u'Африка / Луанда'],
    35 : [u'Africa/Lubumbashi', u'Африка / Лубумбаши'],
    36 : [u'Africa/Lusaka', u'Африка / Лусака'],
    37 : [u'Africa/Malabo', u'Африка / Малабо'],
    38 : [u'Africa/Maputo', u'Африка / Мапуту'],
    39 : [u'Africa/Maseru', u'Африка / Масеру'],
    40 : [u'Africa/Mbabane', u'Африка / Мбабане'],
    41 : [u'Africa/Mogadishu', u'Африка / Могадишо'],
    42 : [u'Africa/Monrovia', u'Африка / Монровия'],
    43 : [u'Africa/Nairobi', u'Африка / Найроби'],
    44 : [u'Africa/Ndjamena', u'Африка / Нджамена'],
    45 : [u'Africa/Niamey', u'Африка / Ниамей'],
    46 : [u'Africa/Nouakchott', u'Африка / Нуакшот'],
    47 : [u'Africa/Ouagadougou', u'Африка / Уагадугу'],
    48 : [u'Africa/Porto-Novo', u'Африка / Порто-Ново'],
    49 : [u'Africa/Sao_Tome', u'Африка / Сан-Томе'],
    50 : [u'Africa/Tripoli', u'Африка / Триполи'],
    51 : [u'Africa/Tunis', u'Африка / Тунис'],
    52 : [u'Africa/Windhoek', u'Африка / Виндхук'],
    53 : [u'America/Adak', u'Америка / Адак'],
    54 : [u'America/Anchorage', u'Америка / Анкоридж'],
    55 : [u'America/Anguilla', u'Америка / Ангилья'],
    56 : [u'America/Antigua', u'Америка / Антигуа'],
    57 : [u'America/Araguaina', u'Америка / Арагуаина'],
    58 : [u'America/Argentina/Buenos_Aires', u'Америка / Аргентина / Буэнос-Айрес'],
    59 : [u'America/Argentina/Catamarca', u'Америка / Аргентина / Катамарка'],
    60 : [u'America/Argentina/Jujuy', u'Америка / Аргентина / Жужуй'],
    61 : [u'America/Argentina/Mendoza', u'Америка / Аргентина / Мендоса'],
    62 : [u'America/Argentina/Salta', u'Америка / Аргентина / Сальта'],
    63 : [u'America/Argentina/San_Juan', u'Америка / Аргентина / Сан Хуан'],
    64 : [u'America/Argentina/San_Luis', u'Америка / Аргентина / Сан Луис'],
    65 : [u'America/Argentina/Tucuman', u'Америка / Аргентина / Тукуман'],
    66 : [u'America/Argentina/Ushuaia', u'Америка / Аргентина / Ушуайя'],
    67 : [u'America/Aruba', u'Америка / Аруба'],
    68 : [u'America/Asuncion', u'Америка / Асунсьон'],
    69 : [u'America/Atikokan', u'Америка / Атикокан'],
    70 : [u'America/Barbados', u'Америка / Барбадос'],
    71 : [u'America/Belem', u'Америка / Белем'],
    72 : [u'America/Belize', u'Америка / Белиз'],
    73 : [u'America/Boa_Vista', u'Америка / Боа-Виста'],
    74 : [u'America/Bogota', u'Америка / Богота'],
    75 : [u'America/Boise', u'Америка / Бойсе'],
    76 : [u'America/Cambridge_Bay', u'Америка / Кеймбридж-Бей'],
    77 : [u'America/Campo_Grande', u'Америка / Кампу-Гранди'],
    78 : [u'America/Cancun', u'Америка / Канкуне'],
    79 : [u'America/Caracas', u'Америка / Каракас'],
    80 : [u'America/Cayenne', u'Америка / Кайенна'],
    81 : [u'America/Cayman', u'Америка / Кайман'],
    82 : [u'America/Chicago', u'America / Чикаго'],
    83 : [u'America/Chihuahua', u'Америка / Чихуахуа'],
    84 : [u'America/Costa_Rica', u'Америка / Коста-Рика'],
    85 : [u'America/Creston', u'Америка / Крестон'],
    86 : [u'America/Cuiaba', u'Америка / Куяба'],
    87 : [u'America/Curacao', u'Америка / Кюрасао'],
    88 : [u'America/Danmarkshavn', u'Америка / Данмаркшавн'],
    89 : [u'America/Dawson', u'Америка / Доусон'],
    90 : [u'America/Denver', u'Америка / Денвер'],
    91 : [u'America/Detroit', u'Америка / Детройт'],
    92 : [u'America/Dominica', u'Америка / Доминика'],
    93 : [u'America/Edmonton', u'Америка / Эдмонтон'],
    94 : [u'America/Eirunepe', u'Америка / Эйрунепе'],
    95 : [u'America/El_Salvador', u'Америка / Сальвадор'],
    96 : [u'America/Fortaleza', u'Америка / Форталеза'],
    97 : [u'America/Godthab', u'Америка / Готхоб'],
    98 : [u'America/Grenada', u'Америка / Гренада'],
    99 : [u'America/Guadeloupe', u'Америка / Гваделупа'],
    100 : [u'America/Guatemala', u'Америка / Гватемала'],
    101 : [u'America/Guayaquil', u'Америка / Гуаякиль'],
    102 : [u'America/Guyana', u'Америка / Гайана'],
    103 : [u'America/Halifax', u'Америка / Галифакс'],
    104 : [u'America/Havana', u'Америка / Гавана'],
    105 : [u'America/Hermosillo', u'Америка / Эрмосильо'],
    106 : [u'America/Indiana/Indianapolis', u'Америка / Индиана / Индианаполис'],
    107 : [u'America/Indiana/Knox', u'Америка / Индиана / Нокс'],
    108 : [u'America/Indiana/Marengo', u'Америка / Индиана / Маренго'],
    109 : [u'America/Indiana/Petersburg', u'Америка / Индиана / Петербург'],
    110 : [u'America/Indiana/Tell_City', u'Америка / Индиана / Телл Сити'],
    111 : [u'America/Indiana/Vevay', u'Америка / Индиана / Вевей'],
    112 : [u'America/Indiana/Vincennes', u'Америка / Индиана / Винсеннес'],
    113 : [u'America/Indiana/Winamac', u'Америка / Индиана / Уинамак'],
    114 : [u'America/Inuvik', u'Америка / Инувик'],
    115 : [u'America/Iqaluit', u'Америка / Икалуит'],
    116 : [u'America/Jamaica', u'Америка / Ямайка'],
    117 : [u'America/Juneau', u'Америка / Джуно'],
    118 : [u'America/Kentucky/Louisville', u'Америка / Кентукки / Луисвилл'],
    119 : [u'America/Kentucky/Monticello', u'Америка / Кентукки / Монтиселло'],
    120 : [u'America/Kralendijk', u'Америка / Кралендейк'],
    121 : [u'America/La_Paz', u'Америка / Ла-Пас'],
    122 : [u'America/Lima', u'Америка / Лима'],
    123 : [u'America/Los_Angeles', u'America /Лос-Анджелес'],
    124 : [u'America/Maceio', u'Америка / Масейо'],
    125 : [u'America/Managua', u'Америка / Манагуа'],
    126 : [u'America/Manaus', u'Америка / Манаус'],
    127 : [u'America/Marigot', u'Америка / Маригот'],
    128 : [u'America/Martinique', u'Америка / Мартиника'],
    129 : [u'America/Matamoros', u'Америка / Матаморос'],
    130 : [u'America/Mazatlan', u'Америка / Масатлан'],
    131 : [u'America/Menominee', u'Америка / меномини'],
    132 : [u'America/Merida', u'Америка / Мерида'],
    133 : [u'America/Metlakatla', u'Америка / Метлейкатла'],
    134 : [u'America/Mexico_City', u'Америка / Мехико'],
    135 : [u'America/Miquelon', u'Америка / Микелон'],
    136 : [u'America/Moncton', u'Америка / Монктон'],
    137 : [u'America/Monterrey', u'Америка / Монтеррее'],
    138 : [u'America/Montevideo', u'Америка / Монтевидео'],
    139 : [u'America/Montreal', u'Америка / Монреаль'],
    140 : [u'America/Montserrat', u'Америка / Монтсеррат'],
    141 : [u'America/Nassau', u'Америка / Нассау'],
    142 : [u'America/New_York', u'Америка / Нью-Йорк'],
    143 : [u'America/Nipigon', u'Америка / Нипигон'],
    144 : [u'America/Nome', u'Америка / Ном'],
    145 : [u'America/Noronha', u'Америка / Норонья'],
    146 : [u'America/North_Dakota/Center', u'Америка / Северная Дакота/ Центр'],
    147 : [u'America/Panama', u'Америка / Панама'],
    148 : [u'America/Pangnirtung', u'Америка / Панглао'],
    149 : [u'America/Paramaribo', u'Америка / Парамарибо'],
    150 : [u'America/Port-au-Prince', u'Америка / Порт - о - Пренс'],
    151 : [u'America/Port_of_Spain', u'Америка / Порт-оф-Спейн'],
    152 : [u'America/Porto_Velho', u'Америка / Порту-Велью'],
    153 : [u'America/Puerto_Rico', u'Америка / Пуэрто-Рико'],
    154 : [u'America/Rainy_River', u'Америка /Рейни Ривер'],
    155 : [u'America/Rankin_Inlet', u'Америка / Ранкин Инлет'],
    156 : [u'America/Recife', u'Америка / Ресифи'],
    157 : [u'America/Regina', u'Америка / Рехина'],
    158 : [u'America/Resolute', u'Америка / Резольют'],
    159 : [u'America/Rio_Branco', u'Америка / Рио-Бранка'],
    160 : [u'America/Santa_Isabel', u'Америка / Санта-Изабел'],
    161 : [u'America/Santarem', u'Америка / Сантарен'],
    162 : [u'America/Santiago', u'Америка / Сантьяго'],
    163 : [u'America/Santo_Domingo', u'Америка / Санто-Доминго'],
    164 : [u'America/Sao_Paulo', u'Америка / Сан-Пауло'],
    165 : [u'America/Scoresbysund', u'Америка / Скорсби'],
    166 : [u'America/Shiprock', u'Америка / Шипрок'],
    167 : [u'America/Sitka', u'Америка / Ситка'],
    168 : [u'America/St_Barthelemy', u'Америка / Сент-Бартелеми'],
    169 : [u'America/St_Johns', u'Америка / Сент-Джонс'],
    170 : [u'America/St_Kitts', u'Америка / Сейнт-Китс'],
    171 : [u'America/St_Lucia', u'Америка / Сент-Люсия'],
    172 : [u'America/St_Vincent', u'Америка / Сейнт-Винсент'],
    173 : [u'America/Swift_Current', u'Америка / Свифт Керрент'],
    174 : [u'America/Tegucigalpa', u'Америка / Тегусигальпа'],
    175 : [u'America/Thule', u'Америка / Туле'],
    176 : [u'America/Thunder_Bay', u'Америка / Тандер-Бей'],
    177 : [u'America/Tijuana', u'Америка / Тихуана'],
    178 : [u'America/Toronto', u'Америка / Торонто'],
    179 : [u'America/Tortola', u'Америка / Тортола'],
    180 : [u'America/Vancouver', u'Америка / Ванкувер'],
    181 : [u'America/Whitehorse', u'Америка / Уайтхорс'],
    182 : [u'America/Winnipeg', u'Америка / Виннипег'],
    183 : [u'America/Yakutat', u'Америка / Якутат'],
    184 : [u'America/Yellowknife', u'Америка / Йеллоунайф'],
    185 : [u'Antarctica/Casey', u'Антарктида / Гора Кейси'],
    186 : [u'Antarctica/Davis', u'Антарктида / Море Дейвиса'],
    187 : [u'Antarctica/DumontDUrville', u'Антарктида / Море Дюрвиля'],
    188 : [u'Antarctica/Mawson', u'Антарктида / Моусон'],
    189 : [u'Antarctica/McMurdo', u'Антарктида / Мак-Мердо'],
    190 : [u'Antarctica/Palmer', u'Антарктида / Палмер'],
    191 : [u'Antarctica/Rothera', u'Антарктида / Станция Ротера'],
    192 : [u'Antarctica/Syowa', u'Антарктида / Сева'],
    193 : [u'Antarctica/Vostok', u'Антарктида / Восток'],
    194 : [u'Arctic/Longyearbyen', u'Арктика / Лонгйир'],
    195 : [u'Asia/Aden', u'Азия / Аден'],
    196 : [u'Asia/Almaty', u'Азия / Алматы'],
    197 : [u'Asia/Amman', u'Азия / Амман'],
    198 : [u'Asia/Anadyr', u'Азия / Анадырь'],
    199 : [u'Asia/Aqtau', u'Азия / Актау'],
    200 : [u'Asia/Aqtobe', u'Азия / Актобе'],
    201 : [u'Asia/Ashgabat', u'Азия / Ашхабад'],
    202 : [u'Asia/Baghdad', u'Азия / Багдад'],
    203 : [u'Asia/Bahrain', u'Азия / Бахрейн'],
    204 : [u'Asia/Baku', u'Азия / Баку'],
    205 : [u'Asia/Bangkok', u'Азия / Бангкок'],
    206 : [u'Asia/Beirut', u'Азия / Бейрут'],
    207 : [u'Asia/Bishkek', u'Азия / Бишкек'],
    208 : [u'Asia/Brunei', u'Азия / Бруней'],
    209 : [u'Asia/Choibalsan', u'Азия / Чойбалсан'],
    210 : [u'Asia/Chongqing', u'Азия / Чунцин'],
    211 : [u'Asia/Colombo', u'Азия / Коломбо'],
    212 : [u'Asia/Damascus', u'Азия / Дамаск'],
    213 : [u'Asia/Dhaka', u'Азия / Дакка'],
    214 : [u'Asia/Dili', u'Азия / Дили'],
    215 : [u'Asia/Dubai', u'Азия / Дубай'],
    216 : [u'Asia/Dushanbe', u'Азия / Душанбе'],
    217 : [u'Asia/Gaza', u'Азия / Газе'],
    218 : [u'Asia/Harbin', u'Азия / Харбин'],
    219 : [u'Asia/Hebron', u'Азия / Хеврон'],
    220 : [u'Asia/Ho_Chi_Minh', u'Азия / Хошимин'],
    221 : [u'Asia/Hong_Kong', u'Азия / Гонконг'],
    222 : [u'Asia/Hovd', u'Азия / Ховд'],
    223 : [u'Asia/Irkutsk', u'Азия / Иркутск'],
    224 : [u'Asia/Jakarta', u'Азия / Джакарта'],
    225 : [u'Asia/Jayapura', u'Азия / Джаяпура'],
    226 : [u'Asia/Jerusalem', u'Азия / Иерусалим'],
    227 : [u'Asia/Kabul', u'Азия / Кабул'],
    228 : [u'Asia/Kamchatka', u'Азия / Камчатка'],
    229 : [u'Asia/Karachi', u'Азия / Карачи'],
    230 : [u'Asia/Kashgar', u'Азия / Кашгар'],
    231 : [u'Asia/Kathmandu', u'Азия / Катманду'],
    232 : [u'Asia/Kolkata', u'Азия / Калькутта'],
    233 : [u'Asia/Krasnoyarsk', u'Азия / Красноярск'],
    234 : [u'Asia/Kuala_Lumpur', u'Азия / Куала-Лумпур'],
    235 : [u'Asia/Kuching', u'Азия / Кучинг'],
    236 : [u'Asia/Kuwait', u'Азия / Кувейт'],
    237 : [u'Asia/Macau', u'Азия / Макао'],
    238 : [u'Asia/Magadan', u'Азия / Магадан'],
    239 : [u'Asia/Makassar', u'Азия / Макассар'],
    240 : [u'Asia/Manila', u'Азия / Манила'],
    241 : [u'Asia/Muscat', u'Азия / Мускат'],
    242 : [u'Asia/Nicosia', u'Азия / Никосия'],
    243 : [u'Asia/Novokuznetsk', u'Азия / Новокузнецк'],
    244 : [u'Asia/Novosibirsk', u'Азия / Новосибирск'],
    245 : [u'Asia/Omsk', u'Азия / Омск'],
    246 : [u'Asia/Phnom_Penh', u'Азия / Пномпень'],
    247 : [u'Asia/Pontianak', u'Азия / Понтианак'],
    248 : [u'Asia/Pyongyang', u', Азия / Пхеньян'],
    249 : [u'Asia/Qatar', u'Азия / Катар'],
    250 : [u'Asia/Qyzylorda', u'Азия / Кызылорда'],
    251 : [u'Asia/Rangoon', u'Азия / Рангун'],
    252 : [u'Asia/Riyadh', u'Азия / Эр-Рияд'],
    253 : [u'Asia/Sakhalin', u'Азия / Сахалин'],
    254 : [u'Asia/Samarkand', u'Азия / Самарканд'],
    255 : [u'Asia/Seoul', u', Азия / Сеул'],
    256 : [u'Asia/Shanghai', u'Азия / Шанхай'],
    257 : [u'Asia/Singapore', u'Азия / Сингапур'],
    258 : [u'Asia/Taipei', u'Азия / Тайбэй'],
    259 : [u'Asia/Tashkent', u'Азия / Ташкент'],
    260 : [u'Asia/Tbilisi', u'Азия / Тбилиси'],
    261 : [u'Asia/Tehran', u'Азия / Тегеран'],
    262 : [u'Asia/Thimphu', u'Азия / Тхимпху'],
    263 : [u'Asia/Tokyo', u', Азия / Токио'],
    264 : [u'Asia/Ulaanbaatar', u'Азия / Улан-Баторе'],
    265 : [u'Asia/Urumqi', u'Азия / Урумчи'],
    266 : [u'Asia/Vientiane', u'Азия / Вьентьян'],
    267 : [u'Asia/Vladivostok', u'Азия / Владивосток'],
    268 : [u'Asia/Yakutsk', u'Азия / Якутск'],
    269 : [u'Asia/Yekaterinburg', u'Азия / Екатеринбург'],
    270 : [u'Asia/Yerevan', u'Азия / Ереван'],
    271 : [u'Atlantic/Azores', u'Атланика / Азорские острова'],
    272 : [u'Atlantic/Bermuda', u'Атлантика / Бермудские острова'],
    273 : [u'Atlantic/Canary', u'Атлантика / Канары'],
    274 : [u'Atlantic/Cape_Verde', u'Атлантика / Кабо-Верде'],
    275 : [u'Atlantic/Faroe', u'Атлантика / Фарерских'],
    276 : [u'Atlantic/Madeira', u'Атлантика / Мадейра'],
    277 : [u'Atlantic/Reykjavik', u'Атлантика / Рейкьявик'],
    278 : [u'Atlantic/South_Georgia', u'Атлантика /Джорджия'],
    279 : [u'Atlantic/St_Helena', u'Атлантика / Святая Елена'],
    280 : [u'Atlantic/Stanley', u'Атлантика / Стэнли'],
    281 : [u'Australia/Adelaide', u'Австралия / Аделаида'],
    282 : [u'Australia/Brisbane', u'Австралия / Брисбен'],
    283 : [u'Australia/Broken_Hill', u'Австралия / Брокен Хилл'],
    284 : [u'Australia/Currie', u'Австралия / Карри'],
    285 : [u'Australia/Darwin', u'Австралия / Дарвин'],
    286 : [u'Australia/Eucla', u'Австралия / Евкла'],
    287 : [u'Australia/Hobart', u'Австралия / Хобарт'],
    288 : [u'Australia/Lindeman', u'Австралия / Линдеман'],
    289 : [u'Australia/Lord_Howe', u'Австралия / Лорд-Хау'],
    290 : [u'Australia/Melbourne', u'Австралия / Мельбурн'],
    291 : [u'Australia/Perth', u'Австралия / Перт'],
    292 : [u'Australia/Sydney', u'Австралия / Сидней'],
    293 : [u'Canada/Atlantic', u'Канада / Атлантика'],
    294 : [u'Canada/Central', u'Канада / Центральная'],
    295 : [u'Canada/Eastern', u'Канада / Восточная'],
    296 : [u'Canada/Mountain', u'Канада / Горная'],
    297 : [u'Canada/Newfoundland', u'Канада / Ньюфаундленд'],
    298 : [u'Canada/Pacific', u'Канада / Тихий океан'],
    299 : [u'Europe/Amsterdam', u'Европа / Амстердам'],
    300 : [u'Europe/Andorra', u'Европа / Андорра'],
    301 : [u'Europe/Athens', u'Европа / Афины'],
    302 : [u'Europe/Belgrade', u'Европа / Белград'],
    303 : [u'Europe/Berlin', u'Европа / Берлин'],
    304 : [u'Europe/Bratislava', u'Европа / Братислава'],
    305 : [u'Europe/Brussels', u'Европа / Брюссель'],
    306 : [u'Europe/Bucharest', u'Европа / Бухарест'],
    307 : [u'Europe/Budapest', u'Европа / Будапеште'],
    308 : [u'Europe/Chisinau', u'Европа / Кишинев'],
    309 : [u'Europe/Copenhagen', u'Европа / Копенгаген'],
    310 : [u'Europe/Dublin', u'Европа / Дублине'],
    311 : [u'Europe/Gibraltar', u'Европа / Гибралтар'],
    312 : [u'Europe/Guernsey', u'Европа / Гернси'],
    313 : [u'Europe/Helsinki', u' в Европе / Хельсинки'],
    314 : [u'Europe/Isle_of_Man', u'Европа / Остров Мэн'],
    315 : [u'Europe/Istanbul', u'Европа / Стамбул'],
    316 : [u'Europe/Jersey', u'Европа / Джерси'],
    317 : [u'Europe/Kaliningrad', u'Европа / Калининград'],
    318 : [u'Europe/Kiev', u'Европа / Киев'],
    319 : [u'Europe/Lisbon', u'Европа / Лиссабон'],
    320 : [u'Europe/Ljubljana', u'Европа / Любляна'],
    321 : [u'Europe/London', u'Европа / Лондон'],
    322 : [u'Europe/Luxembourg', u'Европа / Люксембург'],
    323 : [u'Europe/Madrid', u'Европа / Мадрид'],
    324 : [u'Europe/Malta', u'Европа / Мальта'],
    325 : [u'Europe/Mariehamn', u'Европа / Мариехамн'],
    326 : [u'Europe/Minsk', u'Европа / Минск'],
    327 : [u'Europe/Monaco', u'Европа / Монако'],
    329 : [u'Europe/Oslo', u'Европа / Осло'],
    330 : [u'Europe/Paris', u'Европа / Париж'],
    331 : [u'Europe/Podgorica', u'Европа / Подгорица'],
    332 : [u'Europe/Prague', u'Европа / Прага'],
    333 : [u'Europe/Riga', u'Европа / Рига'],
    334 : [u'Europe/Rome', u'Европа / Рим'],
    335 : [u'Europe/Samara', u'Европа / Самара'],
    336 : [u'Europe/San_Marino', u'Европа / Сан-Марино'],
    337 : [u'Europe/Sarajevo', u'Европа / Сараево'],
    338 : [u'Europe/Simferopol', u'Европа / Симферополь'],
    339 : [u'Europe/Skopje', u'Европа / Скопье'],
    340 : [u'Europe/Sofia', u'Европа / София'],
    341 : [u'Europe/Stockholm', u'Европа / Стокгольм'],
    342 : [u'Europe/Tallinn', u'Европа / Таллин'],
    343 : [u'Europe/Tirane', u'Европа / Тирана'],
    344 : [u'Europe/Uzhgorod', u'Европа / Ужгород'],
    345 : [u'Europe/Vaduz', u'Европа / Вадуц'],
    346 : [u'Europe/Vatican', u'Европа / Ватикан'],
    347 : [u'Europe/Vienna', u'Европа / Вена'],
    348 : [u'Europe/Vilnius', u'Европа / Вильнюс'],
    349 : [u'Europe/Volgograd', u'Европа / Волгоград'],
    350 : [u'Europe/Warsaw', u'Европа / Варшава'],
    351 : [u'Europe/Zagreb', u'Европа / Загреб'],
    352 : [u'Europe/Zaporozhye', u'Европа / Запорожье'],
    353 : [u'Europe/Zurich', u'Европа / Цюрих'],
    354 : [u'Indian/Antananarivo', u'Индийский океан/ Антананариву'],
    355 : [u'Indian/Chagos', u'Индийский океан / Чагос'],
    356 : [u'Indian/Christmas', u'Индийский океан / остров Рождества'],
    357 : [u'Indian/Cocos', u'Индийский океан / Кокос'],
    358 : [u'Indian/Comoro', u'Индийский океан / Коморы'],
    359 : [u'Indian/Kerguelen', u'Индийский океан / Кергелен'],
    360 : [u'Indian/Mahe', u'Индийский океан / Маэ'],
    361 : [u'Indian/Maldives', u'Индийский океан / Мальдивы'],
    362 : [u'Indian/Mauritius', u'Индийский океан / Маврикий'],
    363 : [u'Indian/Mayotte', u'Индийский океан / Майотта'],
    364 : [u'Indian/Reunion', u'Индийский океан / Реюньон'],
    365 : [u'Pacific/Apia', u'Тихий океан / Апиа'],
    366 : [u'Pacific/Auckland', u'Тихий океан / Окленд'],
    367 : [u'Pacific/Chatham', u'Тихий океан / Чатем'],
    368 : [u'Pacific/Chuuk', u'Тихий океан / Чуук'],
    369 : [u'Pacific/Easter', u'Тихий океан / Пасха'],
    370 : [u'Pacific/Efate', u'Тихий океан / Эфате'],
    371 : [u'Pacific/Enderbury', u'Тихий океан / Эндербери'],
    372 : [u'Pacific/Fakaofo', u'Тихий океан / Факаофо'],
    373 : [u'Pacific/Fiji', u'Тихий океан / Фиджи'],
    374 : [u'Pacific/Funafuti', u'Тихий океан / Фунафути'],
    375 : [u'Pacific/Galapagos', u'Тихий океан / Галапагосские острова'],
    376 : [u'Pacific/Gambier', u'Тихий океан / Гамбье'],
    377 : [u'Pacific/Guadalcanal', u'Тихий океан / Гуадалканал'],
    378 : [u'Pacific/Guam', u'Тихий океан / Гуам'],
    379 : [u'Pacific/Honolulu', u'Тихий океан / Гонолулу'],
    380 : [u'Pacific/Johnston', u'Тихий океан / Джонстон'],
    381 : [u'Pacific/Kiritimati', u'Тихий океан / Киритимати'],
    382 : [u'Pacific/Kosrae', u'Тихий океан / Косраэ'],
    383 : [u'Pacific/Kwajalein', u'Тихий океан / Кваджалейн'],
    384 : [u'Pacific/Majuro', u'Тихий океан / Маджуро'],
    385 : [u'Pacific/Marquesas', u'Тихий океан / Маркизские острова'],
    386 : [u'Pacific/Midway', u'Тихий океан / Мидвэй'],
    387 : [u'Pacific/Nauru', u'Тихий океан / Науру'],
    388 : [u'Pacific/Niue', u'Тихий океан / Ниуэ'],
    389 : [u'Pacific/Norfolk', u'Тихий океан / Норфолк'],
    390 : [u'Pacific/Noumea', u'Тихий океан / Нумеа'],
    391 : [u'Pacific/Pago_Pago', u'Тихий океан / Паго-Паго'],
    392 : [u'Pacific/Palau', u', Тихий океан / Палау'],
    393 : [u'Pacific/Pitcairn', u'Тихий океан / Питкэрн'],
    394 : [u'Pacific/Pohnpei', u'Тихий океан / Понпеи'],
    395 : [u'Pacific/Port_Moresby', u'Тихий океан / Порт-Морсби'],
    396 : [u'Pacific/Rarotonga', u'Тихий океан / Раротонга'],
    397 : [u'Pacific/Saipan', u'Тихий океан / Сайпан'],
    398 : [u'Pacific/Tahiti', u'Тихий океан / Таити'],
    399 : [u'Pacific/Tarawa', u'Тихий океан / Тарава'],
    400 : [u'Pacific/Tongatapu', u'Тихий океан / Тонга'],
    401 : [u'Pacific/Wake', u'Тихий океан / Уэйк'],
    402 : [u'Pacific/Wallis', u'Тихий океан / Уоллис'],
    403 : [u'US/Alaska', u'США / Аляска'],
    404 : [u'US/Arizona', u'США / Аризона'],
    405 : [u'US/Central', u'США / Центральный'],
    406 : [u'US/Eastern', u'США / Восточный'],
    407 : [u'US/Hawaii', u'США / Гавайские острова'],
    408 : [u'US/Mountain', u'США / Горный'],
    409 : (u'US/Pacific', u'США / Тихий океан')}

def make_tz_name(id, cur_local_time, cur_locale = 'ru'):
    locale_name = cur_locale.lower()
    if locale_name not in locale_indexes or id not in known_timezones:
        return ''

    locale_index = locale_indexes[locale_name]
    zone_obj = pytz.timezone(known_timezones[id][0])
    zone_time = zone_obj.localize(cur_local_time)
    name = u'(UTC%s) %s' % (zone_time.strftime('%z'), known_timezones[id][locale_index])
    return name.replace('+', ' + ').replace('-', ' - ').replace('_', ' ')

def full_tz_info(short_name, cur_locale = 'ru'):
    locale_name = cur_locale.lower()
    for id, val in known_timezones.iteritems():
        if val[0] == short_name:
            return id, make_tz_name(id, datetime.datetime.now(), locale_name)
    return -1, ''
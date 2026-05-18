import os
BOT_TOKEN = os.getenv("8936348536:AAE9dzoRfWTQfyvwKApM_9IbCo_43UCezlo", "")

ADMIN_IDS = [1432396874]

CHANNELS = [
    {
        "id": "@YIA_Shofirkon_tumani",
        "name": "Shofirkon Yoshlari",
        "invite_link": "https://t.me/YIA_Shofirkon_tumani"
    },
    {
        "id": "@YIABuxoro_viloyat_boshqarmasi",
        "name": "Buxoro Yoshlari",
        "invite_link": "https://t.me/YIABuxoro_viloyat_boshqarmasi"
    },
]

CANDIDATES = [
    {"id": 1,  "name": "Yoqubov Faridun Obloberdi o'g'li",       "mahalla": "G'ulomte"},
    {"id": 2,  "name": "Qahramonov Xurshid Zafarovich",          "mahalla": "Jo'ynav"},
    {"id": 3,  "name": "Arabov Istam Iskandar o'g'li",           "mahalla": "Iskogare"},
    {"id": 4,  "name": "Aslonov Sunnatillo Hamza o'g'li",        "mahalla": "Qalmaqon"},
    {"id": 5,  "name": "Tojiev Erkin Ergashovich",               "mahalla": "Quyi Chuqurak"},
    {"id": 6,  "name": "Baqoev Javohir Sherzod o'g'li",          "mahalla": "Qo'rg'oni Vardonze"},
    {"id": 7,  "name": "Safarov Shahboz Sunnat o'g'li",          "mahalla": "Talisafed"},
    {"id": 8,  "name": "Rashidov Abror Sulaymon o'g'li",         "mahalla": "Sh. Rashidov"},
    {"id": 9,  "name": "Umarov Doston O'tkir o'g'li",            "mahalla": "Chuquraq"},
    {"id": 10, "name": "Komilov Alisher Sadriyevich",            "mahalla": "Yangiqishloq"},
    {"id": 11, "name": "Hoshimov Mardon Ato o'g'li",             "mahalla": "Arabxona"},
    {"id": 12, "name": "Amonov Hudoyor Umidjon o'g'li",          "mahalla": "Boboato"},
    {"id": 13, "name": "Xalilov Muxriddin Bahodir o'g'li",       "mahalla": "Bobur"},
    {"id": 14, "name": "To'xtaqulov Sirojiddin Narzi o'g'li",    "mahalla": "Bog'iafzal"},
    {"id": 15, "name": "Zokirov Baxtiyor Baxshullo o'g'li",      "mahalla": "Jilvon"},
    {"id": 16, "name": "Dilmurodov Jo'rabek Elmurod o'g'li",     "mahalla": "Jo'sho'ra"},
    {"id": 17, "name": "Muzaffarov Abdullo Bobur o'g'li",        "mahalla": "Mirzoqul"},
    {"id": 18, "name": "G'aybulayev Hasan Sayfiddin o'g'li",     "mahalla": "Pashmon"},
    {"id": 19, "name": "Shirinov Muhammad Shayxiddin o'g'li",    "mahalla": "Mazlaxon Chandir"},
    {"id": 20, "name": "Shodiev Rajabboy Habib o'g'li",          "mahalla": "Chitgaron"},
    {"id": 21, "name": "Dilmurodov Eldor Elmurod o'g'li",        "mahalla": "Shodlik"},
    {"id": 22, "name": "Muqimov Shuhrat Zavqiddinovich",         "mahalla": "Denov"},
    {"id": 23, "name": "Yandashev Mashxur Hamro o'g'li",         "mahalla": "Horin"},
    {"id": 24, "name": "Mannonov Elzod Bobir o'g'li",            "mahalla": "Do'rmon"},
    {"id": 25, "name": "Arabov Hamro Quvondiq o'g'li",           "mahalla": "Jo'yrabot"},
    {"id": 26, "name": "Hasanov Dilshod Azamovich",              "mahalla": "Zarchabek"},
    {"id": 27, "name": "Qurbonov Muxlis Mirzo o'g'li",           "mahalla": "Dorigar"},
    {"id": 28, "name": "Toshev Axmedjon Ne'mat o'g'li",          "mahalla": "Ko'rishkent"},
    {"id": 29, "name": "Samadov Oxunjon Hayot o'g'li",           "mahalla": "Qayrag'och"},
    {"id": 30, "name": "Murodov Nodirbek Zafar o'g'li",          "mahalla": "Mahallaqozi"},
    {"id": 31, "name": "Elmurodov Nurali Nurmurod o'g'li",       "mahalla": "Mingchinor"},
    {"id": 32, "name": "Ahmedov Ozod Ramazon o'g'li",            "mahalla": "Navbahor"},
    {"id": 33, "name": "Jo'raboyev Xushnudjon Muqumjon o'g'li",  "mahalla": "Nekkishi"},
    {"id": 34, "name": "Ismoilov Jahongir Odil o'g'li",          "mahalla": "Pattaxon"},
    {"id": 35, "name": "Ramazanov Behruz Bahodir o'g'li",        "mahalla": "Sultonobod"},
    {"id": 36, "name": "Qahhorov Oqiljon Bobomurod o'g'li",      "mahalla": "Temirchi"},
    {"id": 37, "name": "Shirinov Nodirjon Erkin o'g'li",         "mahalla": "Shibirg'on"},
    {"id": 38, "name": "Muqimov Shuxrat Xakimovich",             "mahalla": "Kalon"},
    {"id": 39, "name": "Qamariddinov Akobir Azamat o'g'li",      "mahalla": "Nurafshon"},
    {"id": 40, "name": "Xojiqulov Behruz Burxon o'g'li",         "mahalla": "Alisher Navoiy"},
    {"id": 41, "name": "Sharipov Sherali Tojiboy o'g'li",        "mahalla": "Boboxaydar"},
    {"id": 42, "name": "Muxtorova Nigina Tolib qizi",            "mahalla": "Guliston"},
    {"id": 43, "name": "Teshaev Maruf Maxsud o'g'li",            "mahalla": "Kotiyon"},
    {"id": 44, "name": "Nabiev Nodirjon Qayim o'g'li",           "mahalla": "Savrak"},
    {"id": 45, "name": "Haydarov Aliyor Qayim o'g'li",           "mahalla": "Talisangobod"},
    {"id": 46, "name": "Po'latov Abrorjon Hikmat o'g'li",        "mahalla": "Tezguzar"},
    {"id": 47, "name": "Otamurodov Mirali Shomurod o'g'li",      "mahalla": "Tinchlik"},
    {"id": 48, "name": "Atovullayev Ulug'bek Vahobovich",        "mahalla": "Xoja Orif"},
    {"id": 49, "name": "Juraev Vohid Usmonovich",                "mahalla": "Paxtaobod"},
]

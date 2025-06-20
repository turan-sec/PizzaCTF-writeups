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
INSERT INTO contacts (email, message) VALUES ('test@gmail.com', '1'-- - ', 'test yozuv');
```
Maqsad VALUESdagi ') ni yopishimiz kerak, ```', '1'-- - ``` shu uchun kerak oldingi Quoteni yopib, ikkinchi columnga o'zimizni 1 ni kiritib undan keyingi yozuvni Commentga olish. Lekin baribir o'xshamadi, 

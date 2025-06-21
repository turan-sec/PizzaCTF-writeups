# RACE GROUP

Birinchi navbatda biz login web sahifasiga kiramiz\|  
  
![image.png](<./attachments/3bb97f05deb7aa1b-image.png>)



![image.png](<./attachments/d94a380f49ce04cd-image.png>)

Bu yerda ko'rishimiz mumkunki faqatgina login qismi bor demak royxatdan o'tish qismi ham bolishi kerak va biz signup,sign-up yoki register kabi directorylarni sinab ko'ramiz va bizda register web sahifasi borligi aniqlandi

![image.png](<./attachments/de97ee11cb6867bb-image.png>)

So'ngra biz ro'yxatdan o'tamiz istalgan username, email, passwordlar bilan  
  
![image.png](<./attachments/c14669a5cb833bce-image.png>)

![image.png](<./attachments/a27b6e6bc7727018-image.png>)

Biz ko'rishimiz mumkunki bu yerda faqat forgot password va inbox qismi bor, inbox esa bo'sh chunki inboxga qachonki biz "forgot passwrod" qilganimizda parolni o'zgartirish uchun link keladi  
  
Xo'sh endilikda biz "forgot password" ni sinab korishimiz kerak



![image.png](<./attachments/977cc93afe421823-image.png>)

bu yerda xoxlagan gmail kiritib ko'ramiz

![image.png](<./attachments/fb1227a5cce27986-image.png>)



![image.png](<./attachments/55b6443f86ad45d9-image.png>)

Ko'rishimiz mumkunki user topilmadi, endi rostan ham bor userning gmailini kiritamiz misol uchun o'zimiznikini

![image.png](<./attachments/ec00ee4aaab78a31-image.png>)



![image.png](<./attachments/c17b1bca51035654-image.png>)

Yaxshi! demak bizda user enumuration zafiligi bor !! endilikda biz o'zimizdan kattaroq ruxsatlarga ega userni qidiramiz.  
  
Bu uchun bizga Burp-Suite va Intruder kerak bo'ladi



![image.png](<./attachments/ee30da983ebfc3d8-image.png>)



![image.png](<./attachments/5383d109b4f96c54-image.png>)

Ko'rganimizdek agar valid user bo'lsa 302 response kelmoqda demak bizga malumki "admin@gmail.com" useri mavjud.  
Bizga target aniq endi admin userga chiqish uchun zaiflik qidiramiz. Tepada ko'rganimizedek parolni o'zgartirish uchun timestempda jonatmoqda va hint sifatida home page qismida bir zaiflik beril o'tilgan  
  
![image.png](<./attachments/cf47161f1f4648f7-image.png>)

endi biz adminga ko'tarilishimiz uchun yo'l aniq endi shunchaki zaiflikni sinab ko'rish kerak  
  
Admin useriga ko'tarilish uchun qadamlar  


1. "Forgot password" so'rovini yuborib uni Burp-Suite orqali ushlab oling,uni repeaterga 2 marotaba yuboring va birinchi so'rovga o'zingizni useringiz va ikkinchi so'rovga esa admin userining gmaillarini joylashtiring va so'rovlarni bitta guruh qilish kerak

    - [ ] Sichqonchani requestning ustiga olib borib o'ng tugmasini bosamiz
    - [ ] Add tab to group ustiga borib Create tab groupni bosing

    - [ ] Biz guruh qilmoqchi bo'lgan requestlarni tanlaymiz va "Create" tugmasini bosamiz

![image.png](<./attachments/f6952602c431d979-image.png>)

![image.png](<./attachments/2287c794f015dc94-image.png>)

va bizda shu xabi ko'rinish hosil bo'ladi  
  
![image.png](<./attachments/cfa8b536e07fb08f-image.png>)

so'nga "Send" tugmasini oldidagi tugmani bosamiz  


![Screenshot 2025-06-18 054934.png](<./attachments/94988f20195834ee-Screenshot 2025-06-18 054934.png>)

birinchi so'rovda admin userining gmalini ikkinchi sorovda esa o'zimizning gmailimizni kiriting va jo'nating

![2025-06-18_05-55.png](<./attachments/636d3b0e54121c34-2025-06-18_05-55.png>)

![2025-06-18_05-55_1.png](<./attachments/531a56fe8d1c35ec-2025-06-18_05-55_1.png>)

endi biz o'zimizning userimizning Inboxiga kiramiz va 2 ta bir xil kelgan linkga kiramiz



![2025-06-18_06-02.png](<./attachments/9db2845838e70a09-2025-06-18_06-02.png>)



![2025-06-18_06-03.png](<./attachments/7582f5050dd311df-2025-06-18_06-03.png>)

Yaxshi!! demak biz race-condition zaifligidan foydalanib admin useri uchun token oldik va passwordni o'zgartiramiz

![2025-06-18_06-04.png](<./attachments/5479eed454d2d451-2025-06-18_06-04.png>)

![2025-06-18_06-04_1.png](<./attachments/1f05dc3adebce652-2025-06-18_06-04_1.png>)

endi biz qiladigan ish admin useriga login qilish

![2025-06-18_06-05.png](<./attachments/0ad5791f1d7a2c3c-2025-06-18_06-05.png>)

Bu yerda ko'rib turibmizki bizga yangi qo'shilgan funksiya faqatgina PDF Generator va biz buni exploit qilishimiz kerak

![2025-06-18_06-06.png](<./attachments/dd2a11f8b78c50d5-2025-06-18_06-06.png>)

Exploit qilish uchun qadamlar:  


1. test uchun istalgan matn kiritamiz

    ![Screenshot 2025-06-18 060817.png](<./attachments/a4957d8b1bcd92cc-Screenshot 2025-06-18 060817.png>)
2. Endi biz qaysi pdf generatordan foydalanayotganini aniqlash uchun "exiftoot" ni ishlatamiz

    ![2025-06-18_06-09.png](<./attachments/46784d2dfa5190cb-2025-06-18_06-09.png>)

     Ko'rishimiz mumkunki "wkhtmltopdf 0.12.04" versiyasida ekan endi biz exploit qidiramiz

3. ![image.png](<./attachments/6e70cb23e22545b1-image.png>)

    ```javascript
    <html>
      <body>
        <h1>LFI Test</h1>
        <pre>
          <code>
            <script>
              x = new XMLHttpRequest();
              x.onload = function() {
                document.write(this.responseText);
              };
              x.open("GET", "file:///etc/passwd");
              x.send();
            </script>
          </code>
        </pre>
      </body>
    </html>
    ```

![image.png](<./attachments/665ccb8e7b9b0775-image.png>)

va pdfni ochganda esa

![image.png](<./attachments/e3f916bc0d08bf19-image.png>)

Boom endilikda biz flag.txtni o'qisak bo'lgani



![image.png](<./attachments/76a3e55f05310515-image.png>)

![image.png](<./attachments/e42d1a32b7e236a5-image.png>)

flag: turan{0ops\_u\_g0t\_the\_flag}




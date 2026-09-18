# UX Specification

## 1. Design Goal

The experience should feel like a fun graduation activity, not a clinical questionnaire.

Primary device:

Mobile phone.

---

# 2. Login

Centered card:

```text
🎓

[Event Name]

نام کاربری
[____________]

رمز عبور
[____________]

[ورود]
```

---

# 3. Home

Show:

```text
سلام، علی 👋

چقدر از بچه‌ها رو ارزیابی کردی؟

████████░░ 80%

16 از 20 نفر
```

Buttons:

```text
[نظر دادن درباره بچه‌ها]

[ببین بقیه درباره من چی گفتن]
```

---

# 4. People List

Card:

```text
┌────────────────────────┐
│ Avatar   محمد          │
│                        │
│ 14 نظر ثبت شده         │
│                        │
│ [نظر بده]              │
└────────────────────────┘
```

After rating:

```text
✓ نظر ثبت شده
```

---

# 5. Rating Interface

Show one category at a time or a clean vertically scrollable list.

Example:

```text
محمد چقدر...

خوش‌کشیک

      7

0 ───────●──────── 10

بدکشیک
```

The score should be large and visible.

---

# 6. Memory

At the end:

```text
یه خاطره از محمد داری؟ 👀

[________________________________]

این بخش ناشناس نمایش داده میشه.
```

Large textarea.

---

# 7. Results

Header:

```text
درباره تو چی فکر می‌کنن؟ 👀
```

Then cards:

```text
خوش‌فاز ←→ بدفاز

7.8 / 10

بر اساس 18 نظر
```

Use a horizontal visual indicator.

---

# 8. Memories

```text
خاطره‌ها درباره تو ❤️
```

Cards:

```text
"فلان کشیک هیچ‌وقت یادم نمیره 😂"
```

No author information.

---

# 9. Navigation

Mobile bottom navigation:

```text
🏠 خانه
👥 بچه‌ها
⭐ درباره من
👤 حساب
```

Admin gets a separate admin layout.

---

# 10. Loading

Use skeleton loaders.

Do not show blank pages while data is loading.

---

# 11. Errors

Friendly Persian errors.

Example:

```text
یه مشکلی پیش اومد.
دوباره امتحان کن.
```

Technical errors should only be logged internally.

---

# 12. Confirmation

Before final submission:

```text
آماده‌ای نظرت رو ثبت کنی؟

بعد از ثبت، طبق تنظیمات جشن ممکنه امکان ویرایش وجود داشته باشه.

[ثبت نظر]
[برگرد]
```

---

# 13. Celebration

After completing all participants:

```text
🎉

همه رو ارزیابی کردی!

حالا وقتشه ببینی بقیه درباره خودت چی گفتن 👀

[دیدن نتایج]
```

---

# 14. Accessibility

Support:

- keyboard navigation
- visible focus states
- readable text
- sufficient contrast
- accessible slider labels
- semantic buttons
- RTL layout
# Rating System

## 1. General Rule

Every rating category is a bipolar scale from 0 to 10.

The two endpoints represent opposite characteristics.

Score interpretation:

```text
0 = completely left
5 = balanced / middle
10 = completely right
```

The UI must display both endpoints.

---

# 2. Initial Rating Categories

## Category 1

Left:
خوش‌کشیک

Right:
بدکشیک

Key:
`shift_behavior`

---

## Category 2

Left:
خوش‌فاز

Right:
بدفاز

Key:
`vibe`

---

## Category 3

Left:
گردن‌گیر و کاور

Right:
بندازکن

Key:
`team_support`

---

## Category 4

Left:
سپر بلا

Right:
گردن‌نگیر

Description:
مخصوصاً در مورنینگ

Key:
`morning_responsibility`

---

## Category 5

Left:
مسئولیت‌پذیر

Right:
می‌پیچونه

Key:
`responsibility`

---

## Category 6

Left:
پاویون‌خواب

Right:
باید خونه بخوابم

Key:
`call_room_sleeping`

---

## Category 7

Left:
کشیک‌خر

Right:
کشیک‌فروش

Key:
`shift_preference`

---

## Category 8

Left:
ادایی

Right:
خاکی

Key:
`personality_style`

---

## Category 9

Left:
خوش‌استایل

Right:
بدسلیقه

Key:
`fashion_style`

---

## Category 10

Left:
عمل‌بالا

Right:
سوبر

Key:
`practical_skill`

---

## Category 11

Left:
بامرام

Right:
بی‌معرفت

Key:
`loyalty`

---

## Category 12

Left:
رفیق‌باز

Right:
تنها

Key:
`social_circle`

---

## Category 13

Left:
چیل

Right:
حساس

Key:
`calmness`

---

## Category 14

Left:
پرتلاش

Right:
تنبل

Key:
`work_ethic`

---

## Category 15

Left:
درس‌خون

Right:
کمتر اهل درس

Key:
`study_habits`

Note:
Use a less directly insulting endpoint than "بی‌سواد".

---

## Category 16

Left:
اجتماعی و مذاکره‌گر

Right:
ساکت و سر به زیر

Key:
`social_communication`

---

# 3. Additional Suggested Categories

These should initially be optional and configurable by admin.

## Category 17

Left:
وقت‌شناس

Right:
همیشه دیر

Key:
`punctuality`

---

## Category 18

Left:
منظم

Right:
شلخته

Key:
`organization`

---

## Category 19

Left:
کمک‌حال

Right:
خودش‌محور

Key:
`helpfulness`

---

## Category 20

Left:
شوخ‌طبع

Right:
جدی

Key:
`humor`

---

## Category 21

Left:
پای کار

Right:
جا می‌زنه

Key:
`commitment`

---

## Category 22

Left:
رهبر

Right:
دنبال‌رو

Key:
`leadership`

---

## Category 23

Left:
حاضر جواب

Right:
کم‌حرف

Key:
`communication_style`

---

## Category 24

Left:
خونسرد

Right:
زودجوش

Key:
`emotional_reactivity`

---

## Category 25

Left:
خلاق

Right:
کلاسیک

Key:
`creativity`

---

# 4. Category Configuration

Categories must be stored in the database.

Do not hard-code categories into the frontend.

Each category should have:

- id
- key
- left_label
- right_label
- description
- order
- active
- required
- created_at
- updated_at

---

# 5. Score Validation

Valid scores:

```text
0
1
2
3
4
5
6
7
8
9
10
```

No decimal scores in the initial version.

Backend must reject:

- negative values
- values above 10
- strings
- null when category is required
- invalid category IDs

---

# 6. UI

Recommended slider:

```text
خوش‌کشیک

0    1    2    3    4    5    6    7    8    9    10

بدکشیک
```

The selected number should be clearly visible.

Do not hide the numerical score.

---

# 7. Aggregate Calculation

For each target participant and category:

```text
average = sum(scores) / number_of_scores
```

Round the displayed average to one decimal place.

Example:

```text
7.4 / 10
```

Store the raw individual score as an integer.

---

# 8. Minimum Sample Size

The event configuration should support:

```text
minimum_ratings_for_results
```

Default:

```text
3
```

If fewer than the configured minimum number of ratings exist, the participant should see:

```text
هنوز تعداد نظرات برای نمایش نتیجه کافی نیست.
```

This reduces the possibility of guessing who submitted a rating.

Admin can configure this value.

---

# 9. No Ranking

Do not calculate or expose:

- "best person"
- "worst person"
- global rank
- leaderboard
- winner
- loser

The purpose is personal anonymous feedback, not competition.
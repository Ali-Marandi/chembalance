# برنامهٔ اجرایی و وظایف فنی هفتهٔ دوم کمپین دیجیتال ChemBalance

**هدف هفته:** آزمایش کنترل‌شدهٔ پیام ارزش برای یک مسئلهٔ مشخص و اتصال آن به فعال‌سازی واقعی محصول؛ نه افزایش خام بازدید، نصب یا followers.

**پیش‌شرط ورود:** معیارهای Go هفتهٔ اول باید پاس شده باشند: مسیر رخداد از URL تا فعال‌سازی قابل‌ردیابی است، payloadها متن معادله و PII ندارند، دو کاربر داخلی مسیر را کامل کرده‌اند و build آزمایشی سبز است. اگر حتی یکی از این معیارها Hold باشد، هفتهٔ دوم به رفع کیفیت داده بازمی‌گردد و هیچ آزمایش پیام اجرا نمی‌شود.

> **فرضیهٔ اصلی هفته:** برای مدرس و دستیار آموزشی شیمی، پیامی که «موازنهٔ قابل‌بررسی و کنترل پایستگی» را با یک مسئلهٔ واقعی پیوند می‌دهد، از پیام عمومی «موازنهٔ سریع» کاربرِ فعال‌شونده‌تری جذب می‌کند.

## ۱. محدوده، تصمیم و معیار اصلی

| جزء | تصمیم هفتهٔ دوم | خارج از محدوده |
|---|---|---|
| ICP | مدرس، TA و دانشجوی درس پایهٔ شیمی در آموزش عالی | هم‌زمان هدف‌گیری آزمایشگاه‌های سازمانی، ناشر و بازار عمومی |
| مسئله | ورود و کنترل واکنش یونی یا واکنش دارای گروه تو‌در‌تو | مسئله‌های متعدد، pages پراکنده و landing برای هر feature |
| پیام A | «موازنه را قابل‌بررسی کنید؛ اتم‌ها و بار را در یک نگاه کنترل کنید.» | ادعای کاهش خطا، افزایش نمره یا برتری عددی بدون داده |
| پیام B | «ضرایب صحیح، کنترل پایستگی و خروجی محلی برای تمرین و تدریس شیمی.» | تخفیف، قیمت یا urgency مصنوعی |
| CTA | «یک مثال واقعی را اجرا کنید» | فرم طولانی، درخواست اطلاعات حساس، یا CTAهای متعدد |
| شاخص اصلی | نسبت `activation_completed / attributed_first_opened` | تعداد impression، likes یا page view به‌تنهایی |

این آزمایش به‌تنهایی قرار نیست «برندهٔ آماری نهایی» تعیین کند. در ترافیک کم، هدف کشف signal است: آیا پیام مناسب کاربر را به یک workflow کامل نزدیک می‌کند؟ تصمیم قطعی فقط پس از دادهٔ کافی، مشاهدهٔ کیفی و کیفیت attribution گرفته می‌شود.

## ۲. قرارداد اندازه‌گیری و instrumentation هفتهٔ دوم

### ۲.۱. رخدادها و خواص جدید

هفتهٔ اول رخدادهای پایه را فراهم می‌کند. در هفتهٔ دوم، فقط فیلدهای لازم برای تشخیص variant و مسیر ارزش افزوده می‌شوند.

| رخداد | فیلد جدید | مقدارهای مجاز | هدف |
|---|---|---|---|
| `landing_view` | `landing_variant` | `control`, `verified_balance` | نسبت‌دادن پیام به session |
| `cta_clicked` | `cta_id`, `landing_variant` | `run_example`, `download_desktop` | فهم محل شروع intent |
| `example_opened` | `example_id`, `entry_variant` | `ionic_redox`, `nested_formula`, `unknown` | اتصال page به رفتار محصول |
| `equation_balanced` | `input_mode`, `entry_variant` | `example`, `manual`; variant یا `unknown` | تفکیک استفادهٔ واقعی از کلیک |
| `activation_completed` | `entry_variant`, `time_to_value_bucket` | variant؛ `<60s`, `60–180s`, `>180s` | metric اصلی آزمایش |
| `feedback_submitted` | `prompt_id`, `response_category` | `clarity`, `trust`, `install_friction`, `other` | شواهد کیفی بدون متن/PII اجباری |

### ۲.۲. قواعد attribution

هر landing URL باید با UTM ثابت تولید شود. `utm_content` تنها محل تعیین variant است: `value_control` یا `verified_balance`. این مقدار باید در session storage صفحه نگه‌داری و در مسیر download/installer به شکل query string یا یک attribution token امن منتقل شود. برنامهٔ دسکتاپ token را فقط برای تنظیم `entry_variant` رخدادهای محلی می‌خواند و نباید query کامل یا اطلاعات فرعی URL را ارسال کند.

```text
https://example.invalid/ionic-balance?
  utm_source=partner_outreach&
  utm_medium=email&
  utm_campaign=cb_w2_message_validation&
  utm_content=verified_balance
```

**کنترل فنی:** اگر variant مقدار خارج از allow-list داشته باشد، event با `entry_variant=unknown` ذخیره شود. هرگز variant یا source دلخواه را مستقیماً وارد dashboard SQL نکنید. اگر attribution token منقضی یا نامعتبر باشد، محصول باید همچنان کار کند و فقط attribution را unknown اعلام کند.

### ۲.۳. query کنترل کیفیت

| کنترل | شرط | نتیجهٔ پذیرفته‌شده |
|---|---|---|
| ترتیب قیف | `activation_completed` بعد از `equation_balanced` و `conservation_checked` است | ۱۰۰٪ رخدادهای activation ترتیب منطقی دارند |
| یکتایی | یک install برای یک interaction cycle یک activation دارد | duplicate rate صفر یا دارای دلیل ثبت‌شده |
| integrity variant | هر event منتسب variant معتبر دارد یا `unknown` است | مقدار غیرمجاز صفر است |
| privacy | نمونهٔ payload فاقد formula، email، IP raw یا device fingerprint است | هیچ دادهٔ ممنوع دیده نمی‌شود |
| attribution | هر test link به `landing_view` با source/medium/campaign منتهی می‌شود | link leak یا UTM drop ثبت و رفع می‌شود |
| build parity | version وب/installer در dashboard با release candidate هم‌خوان است | mismatch نسخه صفر است |

## ۳. برنامهٔ روزبه‌روز

### روز ۸ — مرور Go، freeze baseline و ثبت آزمایش

| زمان | کار دقیق | مالک | خروجی | معیار پذیرش |
|---|---|---|---|---|
| ۰۹:۰۰–۰۹:۴۵ | مرور گزارش هفتهٔ اول و تعیین Go/Hold | Product/Growth Lead + Engineer | تصمیم ثبت‌شده و فهرست blocking issue | همهٔ معیارهای Go هفتهٔ اول پاسخ روشن دارند |
| ۰۹:۴۵–۱۰:۳۰ | freeze schema رخدادها برای آزمایش | Data/Operations | event contract v1.1 | نام eventهای پایه در طول هفته تغییر نمی‌کند |
| ۱۰:۳۰–۱۲:۰۰ | ثبت experiment brief | Growth Lead | hypothesis، variants، CTA، metric، source list، stop rule | یک owner و یک metric اصلی دارد |
| ۱۳:۰۰–۱۴:۳۰ | استخراج baseline داخلی | Data/Operations | dashboard snapshot قبل از experiment | timestamp و query ذخیره شده‌اند |
| ۱۴:۳۰–۱۵:۳۰ | security/privacy check attribution token | Engineer | checklist و test case | token شامل PII یا secret نیست |
| ۱۵:۳۰–۱۶:۱۵ | تعیین مسیر escalation | همهٔ مالک‌ها | فهرست incident و SLA داخلی | owner هر failure روشن است |

**Task فنی P0:** یک feature flag به نام `message_validation_week_2` در landing و installer attribution ایجاد کنید. هدف feature flag، rollback بدون تغییر hard-coded URL است. مقدار default باید `false` یا `control` باشد تا بازگشت امن ممکن باشد.

### روز ۹ — طراحی پیام، صفحه و asset علمی

| زمان | کار دقیق | مالک | خروجی | معیار پذیرش |
|---|---|---|---|---|
| ۰۹:۰۰–۱۰:۰۰ | بازنویسی value proposition | Product + Content | message matrix یک‌صفحه‌ای | هر variant یک promise، یک proof و یک CTA دارد |
| ۱۰:۰۰–۱۱:۰۰ | انتخاب مثال علمی واحد | Scientific Reviewer + Content | equation، expected result و scope note | همهٔ اعداد و syntax با محصول تست شده‌اند |
| ۱۱:۰۰–۱۲:۰۰ | ساخت copy variant A و B | Content | headline، subhead، CTA و caption | طول و ساختار دو variant نزدیک‌اند |
| ۱۳:۰۰–۱۴:۳۰ | ساخت asset تصویری محصول | Design | یک اسکرین‌شات یا GIF کوتاه واقعی | هیچ UI/feature خیالی نشان داده نمی‌شود |
| ۱۴:۳۰–۱۵:۳۰ | accessibility review | Design + Content | alt text، contrast، keyboard path | CTA و disclaimer بدون color-only cue قابل‌فهم‌اند |
| ۱۵:۳۰–۱۶:۰۰ | approval علمی و محصول | Scientific Reviewer + Growth Lead | sign-off | ادعای safety/feasibility یا performance بی‌پایه حذف شده است |

**قالب پیام:**
- Variant A: «موازنه را قابل‌بررسی کنید.»
- Proof: «ChemBalance ضرایب، کنترل اتم‌ها و بار خالص را در یک فضای کاری محلی نشان می‌دهد.»
- CTA: «مثال یونی را اجرا کنید.»

- Variant B: «ضرایب صحیح را با اطمینان بررسی کنید.»
- Proof: «ورودی روشن، نتیجهٔ موازنه‌شده، کنترل پایستگی و خروجی محلی.»
- CTA: «مثال یونی را اجرا کنید.»

### روز ۱۰ — پیاده‌سازی landing variants و مسیر دانلود

| زمان | کار دقیق | مالک | خروجی | معیار پذیرش |
|---|---|---|---|---|
| ۰۹:۰۰–۱۰:۳۰ | ساخت variant A با template مشترک | Web/Content Owner | route یا flag variant A | content و CTA طبق brief هستند |
| ۱۰:۳۰–۱۲:۰۰ | ساخت variant B با همان layout | Web/Content Owner | route یا flag variant B | تنها message asset و copy تغییر کرده‌اند |
| ۱۳:۰۰–۱۴:۰۰ | پیاده‌سازی UTM parser و allow-list | Engineer | parser تست‌شده | variant غیرمجاز به unknown map می‌شود |
| ۱۴:۰۰–۱۵:۰۰ | route به download/demo | Web/Engineer | URL انتقال و CTA event | UTM و variant در redirect حفظ می‌شوند |
| ۱۵:۰۰–۱۶:۰۰ | smoke test responsive | QA + Design | ماتریس browser/device | پیام، CTA و scope notice در viewportهای اصلی دیده می‌شوند |
| ۱۶:۰۰–۱۶:۳۰ | production-readiness review | Growth Lead | Go/hold برای instrumentation | هیچ link بدون UTM باقی نمانده است |

**پذیرش فنی landing:** کنترل باید با query parameter مانند `?variant=control` فقط در محیط staging قابل‌اجرا باشد. تولیدکنندهٔ URL باید server-side یا build-time mapping استفاده کند؛ از واردکردن مستقیم نام variant توسط کاربر برای تصمیم‌های حساس پرهیز کنید. اگر analytics endpoint خطا دهد، صفحه و CTA باید بدون تاخیر قابل‌استفاده بمانند.

### روز ۱۱ — اتصال داده، dashboard و QA end-to-end

| زمان | کار دقیق | مالک | خروجی | معیار پذیرش |
|---|---|---|---|---|
| ۰۹:۰۰–۱۰:۳۰ | اتصال `landing_variant` به dashboard | Data/Operations | funnel شکسته‌شده بر اساس variant | variantها جدا و unknown مشخص است |
| ۱۰:۳۰–۱۲:۰۰ | QA برای CTA، download و first-open | Engineer + QA | runbook دو مسیر | control و verified_balance هر دو کامل می‌شوند |
| ۱۳:۰۰–۱۴:۰۰ | تست negative attribution | Engineer | test log | token نامعتبر، UTM ناقص و variant غیرمجاز safe fail می‌شوند |
| ۱۴:۰۰–۱۵:۰۰ | کنترل latency و failure analytics | Engineer | test evidence | failure analytics مسیر product را block نمی‌کند |
| ۱۵:۰۰–۱۶:۰۰ | privacy sampling | Data + Product | نمونهٔ redacted events | field ممنوع در payload نیست |
| ۱۶:۰۰–۱۶:۳۰ | ثبت baseline و release candidate | Data + Engineer | snapshot + build id | dashboard و app version با هم match هستند |

### روز ۱۲ — توزیع محدود، کنترل‌شده و قابل‌ردیابی

| زمان | کار دقیق | مالک | خروجی | معیار پذیرش |
|---|---|---|---|---|
| ۰۹:۰۰–۰۹:۳۰ | بازبینی source list | Growth Lead | فهرست محدود کانال‌های مجاز | کانال‌ها به ICP مرتبط‌اند |
| ۰۹:۳۰–۱۱:۰۰ | آماده‌سازی ۱۰–۲۰ outreach شخصی | Community Lead | پیام شخصی با link اختصاصی | بدون ارسال انبوه و بدون ادعای اثبات‌نشده |
| ۱۱:۰۰–۱۲:۰۰ | انتشار یک محتوای مسئله‌محور | Content | مقاله/ویدیو با CTA واحد | URL و UTM تست شده‌اند |
| ۱۳:۰۰–۱۴:۰۰ | فعال‌سازی partner/referral link | Community Lead | link registry | هر شریک source مشخص دارد |
| ۱۴:۰۰–۱۵:۳۰ | مانیتور daily funnel | Data + Growth | snapshot ۱ | anomaly در کمتر از یک روز دیده می‌شود |
| ۱۵:۳۰–۱۶:۰۰ | تصمیم ادامهٔ توزیع | Growth Lead | log تصمیم | اگر integrity داده مشکل دارد، توزیع pause می‌شود |

**قاعدهٔ کانال:** هفتهٔ دوم همچنان مرحلهٔ کشف است؛ paid acquisition فقط در هفتهٔ ۱۱ و پس از evidence فعال‌سازی بررسی می‌شود. outreach باید به شخص، دوره یا مسئلهٔ واقعی اشاره کند و رضایت دریافت پیام و امکان opt-out را رعایت کند.

### روز ۱۳ — شواهد کیفی، رفع اصطکاک و تحلیل cohort اولیه

| زمان | کار دقیق | مالک | خروجی | معیار پذیرش |
|---|---|---|---|---|
| ۰۹:۰۰–۱۰:۰۰ | انتخاب کاربران/مخاطبان برای گفت‌وگو | Product + Community | دعوت سه گفت‌وگوی کوتاه | هیچ دادهٔ contact بدون رضایت استفاده نمی‌شود |
| ۱۰:۰۰–۱۲:۰۰ | انجام discovery/activation interview | Product | یادداشت ساختاریافته | مسئله، زبان کاربر و obstacle ثبت می‌شوند |
| ۱۳:۰۰–۱۴:۰۰ | بررسی cohort control در برابر variant | Data | cohort view | denominatorها و unknownها مشخص‌اند |
| ۱۴:۰۰–۱۵:۰۰ | triage بزرگ‌ترین اصطکاک | Engineer + Product | P0/P1 fix list | یک اصلاح با بیشترین اثر انتخاب شود |
| ۱۵:۰۰–۱۶:۰۰ | اجرای/آزمون fix محدود | Engineer | patch یا experiment follow-up | regression test یا UI smoke test سبز است |
| ۱۶:۰۰–۱۶:۳۰ | ترکیب evidence کمی و کیفی | Growth Lead | learning memo | نتیجه‌گیری از یک metric منفرد ممنوع است |

### روز ۱۴ — تصمیم و handoff به هفتهٔ سوم

| زمان | کار دقیق | مالک | خروجی | معیار پذیرش |
|---|---|---|---|---|
| ۰۹:۰۰–۱۰:۳۰ | review experiment | همهٔ مالک‌ها | گزارش مختصر experiment | هدف، داده، limitations و تصمیم مشخص‌اند |
| ۱۰:۳۰–۱۱:۳۰ | انتخاب پیام/صفحهٔ بعدی | Growth Lead + Product | تصمیم retain/iterate/stop | هیچ variant بدون دلیل نگه‌داری نمی‌شود |
| ۱۳:۰۰–۱۴:۰۰ | backlog هفتهٔ ۳ | Product + Content | یک asset مسئله‌محور و یک CTA | scope هفتهٔ بعد تک‌هدفه است |
| ۱۴:۰۰–۱۵:۰۰ | مرور داده و privacy | Data + Engineer | retention/cleanup check | test data غیرلازم حذف یا ناشناس‌سازی می‌شود |
| ۱۵:۰۰–۱۶:۰۰ | گزارش مدیریتی ۱ صفحه‌ای | Growth Lead | summary برای سرمایه‌گذار/تیم | بدون ادعای آماری فراتر از sample |

## ۴. طراحی آزمایش و قواعد تصمیم

### ۴.۱. brief اجباری قبل از شروع

| فیلد | مقدار مورد نیاز |
|---|---|
| Experiment ID | `CB-W2-MSG-01` |
| فرضیه | پیام کنترل‌پذیری پایستگی، activation بهتری از پیام عمومی می‌سازد. |
| مخاطب | مدرس/TA/دانشجوی آموزش عالی با مسئلهٔ موازنهٔ واقعی. |
| variantها | `control` و `verified_balance` با layout یکسان. |
| CTA | اجرای مثال یونی / دریافت نسخه. |
| metric اصلی | `activation_completed / attributed_first_opened`. |
| metricهای محافظ | error rate، time-to-value، unknown attribution rate و privacy incidents. |
| بازهٔ زمانی | یک هفته یا تا رسیدن به حجم مشاهده‌شدهٔ از پیش تعیین‌شده، هرکدام دیرتر است. |
| توقف | privacy incident، data integrity failure، build failure یا افزایش معنادار error به‌نسبت baseline داخلی. |

### ۴.۲. گزارش نتیجه بدون فریب آماری

در گزارش، برای هر variant موارد زیر را بنویسید: تعداد landing view، CTA click، first-open منتسب، activation کامل، time-to-value median، error count، تعداد گفت‌وگو و sample limitations. اگر sample پایین است، عبارت «نشانهٔ اولیه» به‌کار ببرید، نه «برنده». اگر attribution `unknown` بالا باشد، هر تفسیر channel/variant متوقف می‌شود تا مشکل فنی رفع شود.

## ۵. backlog فنی هفتهٔ دوم

| اولویت | ticket | جزئیات فنی | شرط پذیرش |
|---|---|---|---|
| P0 | `GROW-201` | allow-list UTM/variant و token attribution | input نامعتبر safe fail و test پوشش دارد |
| P0 | `GROW-202` | eventهای variant و activation metric | ترتیب event و privacy در تست assert می‌شود |
| P0 | `GROW-203` | dashboard funnel variant-aware | control، variant و unknown جدا هستند |
| P0 | `GROW-204` | kill switch/feature flag | بدون deploy code مسیر قابل‌خاموش‌کردن است |
| P1 | `GROW-205` | quick-start روی مثال یونی | user به کمتر از یک دقیقه ارزش اول می‌رسد یا علت failure ثبت می‌شود |
| P1 | `GROW-206` | feedback prompt اختیاری و privacy-safe | response category بدون PII ذخیره می‌شود |
| P2 | `GROW-207` | گزارش cohort export | CSV/داشبورد شامل definition و timestamp است |

## ۶. RACI هفتهٔ دوم

| فعالیت | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| پیام و experiment brief | Content/Growth | Growth Lead | Scientific Reviewer | تیم محصول |
| instrumentation و attribution | Engineer | Product Lead | Data/Operations | Growth Lead |
| dashboard و quality query | Data/Operations | Growth Lead | Engineer | تیم محصول |
| landing deployment | Web/Content | Product Lead | Engineer/Design | Community Lead |
| outreach محدود | Community Lead | Growth Lead | Content | Product Lead |
| Go/Hold و گزارش هفته | Growth Lead | بنیان‌گذار | همهٔ نقش‌ها | سرمایه‌گذار/مشاور در صورت نیاز |

## ۷. خطرها و واکنش‌ها

| خطر | علائم | اقدام فوری |
|---|---|---|
| حجم مشاهده پایین | کمتر از حداقل دادهٔ عملیاتی یا گفت‌وگوی کیفی | دوره را طولانی کنید یا distribution هدفمند را افزایش دهید؛ conclusion آماری ندهید |
| پیام از محصول جداست | CTA زیاد است اما `equation_balanced` پایین | proof/quick-start را اصلاح کنید، نه headline را بارها تغییر دهید |
| تداخل variant | یک کاربر هر دو message را می‌بیند | assignment را در session پایدار و در گزارش user-level dedupe کنید |
| attribution ناقص | `unknown` یا direct غیرعادی بالا | توزیع را pause و link/token flow را اصلاح کنید |
| ادعای علمی بیش از دامنه | برداشت safety/feasibility در feedback | scope notice و wording را همان روز اصلاح کنید |
| telemetry مزاحم تجربه | latency یا crash در event call | async/no-op fallback فعال و ارسال غیرضروری حذف شود |

## ۸. خروجی‌های اجباری پایان هفتهٔ دوم

1. experiment brief امضاشده برای `CB-W2-MSG-01`.
2. دو landing variant کنترل‌شده با یک CTA و یک مثال علمی تأییدشده.
3. attribution token/UTM allow-list، test negative و feature flag rollback.
4. dashboard variant-aware و گزارش کنترل quality.
5. یادداشت سه گفت‌وگوی discovery یا دلیل مستند برای عدم امکان انجام آن.
6. learning memo شامل evidence کمی/کیفی، limitationها و تصمیم هفتهٔ سوم.
7. backlog اولویت‌دار فقط با یک فرضیهٔ اصلی برای هفتهٔ سوم.

## افشای مبنا و محدودیت‌ها

این برنامه، هفتهٔ دوم نقشهٔ ۹۰روزهٔ ChemBalance را به آزمایش message-to-activation تبدیل می‌کند. baseline واقعی CAC، conversion، retention یا حجم کانال هنوز وجود ندارد؛ همهٔ نسبت‌ها باید پس از اندازه‌گیری گزارش شوند. این برنامه از اصل محتوای مردم‌محور و onboarding ساختارمند استفاده می‌کند، اما تضمین رشد یا conversion ارائه نمی‌کند.[1] [2]

## منابع

[1]: https://developers.google.com/search/docs/fundamentals/creating-helpful-content "Google Search Central — Creating Helpful, Reliable, People-First Content"
[2]: https://www.gainsight.com/blog/customer-onboarding/ "Gainsight — Customer Onboarding: Best Practices and Actionable Tips"

# برنامهٔ اجرایی و وظایف فنی هفتهٔ سوم کمپین دیجیتال ChemBalance

**بازه:** روزهای ۱۵ تا ۲۱ برنامهٔ ۹۰روزه  
**وضعیت مبنا:** ۲۸ اوت ۲۰۲۶  
**هدف هفته:** تبدیل نخستین موازنهٔ معتبر به یک نتیجهٔ آموزشی قابل‌استفاده در ماژول «Analysis & charts»؛ بدون گسترش هم‌زمان ICP، کانال، قیمت‌گذاری یا هزینهٔ تبلیغاتی.

> **اصل راهبر:** هفتهٔ سوم یک آزمایش فعال‌سازی و یادگیری است، نه اثبات رشد. محتوا باید به حل یک مسئلهٔ واقعی برای مخاطب آموزش عالی کمک کند و onboarding باید کاربر را به نخستین ارزش محصول برساند؛ نه اینکه همهٔ قابلیت‌ها را در یک تور شلوغ نمایش دهد.[1] [2]

## ۱. پیش‌شرط ورود و تصمیم عملیاتی

ورود به این هفته تنها پس از بسته‌شدن یادداشت یادگیری `CB-W2-MSG-01` مجاز است. خروجی هفتهٔ دوم باید شامل وضعیت کیفیت attribution، تعریف denominatorها، فهرست رخدادهای `unknown`، نتیجهٔ مشاهدهٔ کیفی و تصمیم retain/iterate/stop برای پیام باشد. در زمان تدوین این سند، هیچ نتیجهٔ واقعی CAC، conversion، retention، تعداد نصب یا برندهٔ آماری از هفتهٔ دوم در اختیار نیست؛ بنابراین همهٔ مقادیر baseline در این برنامه **pending measurement** هستند.

| شرط ورود | شاهد مورد نیاز | تصمیم در نبود شاهد |
|---|---|---|
| ترتیب رخدادهای پایه معتبر است | گزارش QA هفتهٔ اول/دوم: `equation_balanced → conservation_checked → activation_completed` | Hold؛ ابتدا instrumentation اصلاح شود. |
| attribution پیام هفتهٔ دوم سالم است | مقدارهای variant فقط از allow-list یا `unknown` هستند؛ trace نمونهٔ URL تا first-open موجود است | Hold؛ توزیع جدید آغاز نشود. |
| مسیر علمی منتخب تأیید شده است | بازبین علمی، مثال و wording را امضا کرده است | Hold؛ asset یا prompt در محصول منتشر نشود. |
| build و UI smoke سبز است | گزارش CI و تست headless نسخهٔ کاندید | Hold؛ آزمایش نباید نقص محصول را پنهان کند. |
| حفاظت داده برقرار است | نمونهٔ payload فاقد formula text، PII، IP خام، stack trace و fingerprint است | Stop و حذف/اصلاح دادهٔ ناسازگار. |

اگر دادهٔ هفتهٔ دوم هنوز کامل نشده، هفتهٔ سوم فقط برای تکمیل measurement، QA و انجام مشاهدهٔ داخلی استفاده می‌شود. هیچ ادعای «پیام برنده»، «بهبود conversion» یا «کاهش اصطکاک» تا زمانی که داده و مشاهدهٔ کیفی هم‌سو نشده‌اند، مجاز نیست.

## ۲. محدوده، فرضیه و معیار اصلی

| جزء | تصمیم هفتهٔ سوم | خارج از محدوده |
|---|---|---|
| ICP | مدرس، دستیار آموزشی و دانشجوی درس پایهٔ شیمی در آموزش عالی | آزمایشگاه‌های سازمانی، ناشر، مدارس و بازار عمومی به‌صورت هم‌زمان |
| مسئلهٔ واحد | کاربر پس از دیدن موازنه و کنترل پایستگی، مسیر واضحی برای تحلیل درصد جرمی یا تبدیل جرم‌به‌جرمِ همان مثال ندارد | آموزش کامل همهٔ قابلیت‌ها، pricing، CRM یا برنامهٔ referral |
| workflow واحد | «یک مثال تأییدشده را موازنه کن، تحلیل را باز کن، و یک نتیجهٔ تحلیلی را ببین» | ورود آزاد به چند مثال/چند persona در یک session |
| CTA واحد | «تحلیل مثال را ببین» | فرم lead، درخواست ایمیل، دانلود اجباری یا CTAهای هم‌زمان |
| asset محتوا | یک راهنمای مسئله‌محور کوتاه با نتیجهٔ قابل‌بررسی و scope notice | تولید انبوه مقاله یا محتوای صرفاً جست‌وجومحور |
| metric اصلی | `analysis_activation_completed / onboarding_eligible_first_opens` | impression، follower، page view، download یا duration به‌تنهایی |

> **فرضیهٔ اصلی `CB-W3-ONB-01`:** برای ICP آموزشیِ هفته‌های قبل، یک مسیر opt-in و تک‌مرحله‌ای که پس از موازنهٔ معتبر، کاربر را به تحلیل همان مثال هدایت می‌کند، نسبت به کشف آزاد قابلیت‌ها، evidence بیشتری از تکمیل یک نتیجهٔ تحلیلی ایجاد می‌کند.

این فرضیه، **علّیت یا uplift عددی را پیشاپیش فرض نمی‌گیرد**. اگر امکان اجرای مسیر مقایسه‌ای کنترل‌شده وجود نداشته باشد، خروجی هفته صرفاً شواهد توصیفی از محل اصطکاک و فهم کاربر خواهد بود. انجام onboarding به‌شکل پیوسته، مشاهدهٔ نقاط ریزش و ترکیب analytics با مصاحبهٔ کاربر، با راهنمای پژوهش onboarding سازگار است.[2]

## ۳. تعریف عملیاتی ارزش، cohort و metricها

### ۳.۱. state machine فعال‌سازی تحلیلی

مبنای فعال‌سازی هفتهٔ اول همچنان معتبر است. هفتهٔ سوم فقط یک لایهٔ ثانویه و مستقل اضافه می‌کند؛ بنابراین تغییر تعریف قدیمی `activation_completed` ممنوع است.

```text
app_first_opened
  → example_opened (approved example)
  → equation_balanced (valid result)
  → conservation_checked (valid result)
  → onboarding_prompt_eligible
  → analysis_workspace_opened
  → composition_calculated OR mass_flow_calculated
  → analysis_activation_completed
```

`onboarding_prompt_eligible` صرفاً پس از موازنه و کنترل پایستگی معتبر و فقط یک‌بار در هر `anonymous_install_id` صادر می‌شود. کاربر باید بتواند prompt را ببندد، از آن عبور کند یا مسیر را بعداً باز کند؛ بستن prompt نباید خطا، محدودیت محصول یا ارسال داده ایجاد کند. `analysis_activation_completed` تنها در زمانی ثبت می‌شود که یک نتیجهٔ واقعی ماژول تحلیل نمایش داده شده باشد، نه با کلیک روی tab یا بازشدن tooltip.

### ۳.۲. قرارداد رخدادهای جدید

تمام رخدادها بر قرارداد هفتهٔ اول تکیه می‌کنند: `anonymous_install_id` تصادفی و local-first، `consent_state` صریح، ارسال فقط با `analytics_opt_in`، و عدم ارسال متن equation یا formula. فیلدهای زیر allow-list هستند؛ مقدار خارج از allow-list باید به `unknown` نگاشت شود و به‌هیچ‌وجه در query خام dashboard استفاده نشود.

| رخداد | trigger دقیق | خصوصیات مجاز | دادهٔ صریحاً ممنوع |
|---|---|---|---|
| `onboarding_prompt_eligible` | state machine پس از `conservation_checked` معتبر | `workflow_id=balance_to_analysis`, `entry_variant`, `prompt_version` | متن واکنش، formula، نام species، وزن، PII |
| `onboarding_prompt_actioned` | کاربر یکی از عمل‌های allow-list را انتخاب می‌کند | `action=open_analysis/dismiss/later`, `prompt_version` | متن feedback، coordinate کلیک، fingerprint |
| `analysis_workspace_opened` | صفحهٔ Analysis & charts واقعاً نمایش داده می‌شود | `entry_path=prompt/navigation`, `workflow_id` | title یا URL کامل، formula |
| `composition_calculated` | جدول درصد جرمی برای ورودی معتبر render می‌شود | `result_kind=composition`, `element_count_bucket=1_2/3_4/5_plus`, `workflow_id` | نماد عنصر، مقدار درصد، formula |
| `mass_flow_calculated` | نتیجهٔ mass-to-mass معتبر render می‌شود | `result_kind=mass_flow`, `source_side=reactant/product`, `workflow_id` | گونهٔ انتخاب‌شده، جرم ورودی/خروجی، equation |
| `analysis_activation_completed` | اولین `composition_calculated` یا `mass_flow_calculated` بعد از مسیر مجاز | `completion_kind=composition/mass_flow`, `time_to_analysis_bucket` | مدت دقیق شناسه‌پذیر، formula، PII |
| `onboarding_feedback_submitted` | پاسخ اختیاری دسته‌بندی‌شده ثبت می‌شود | `response_category=clarity/trust/navigation/install_friction/other`, `workflow_id` | free-text ارسالی، email، نام، course |
| `content_asset_opened` | asset تأییدشده از URL/QR مجاز باز می‌شود | `asset_id`, `source_channel`, `entry_variant` | URL کامل، referrer خام، PII |

**قاعدهٔ dedupe:** برای هر install و هر `workflow_id`، حداکثر یک `analysis_activation_completed` در دورهٔ گزارش ثبت می‌شود. تکرار محاسبات باید در view جداگانهٔ engagement شمارش شود، نه در numerator فعال‌سازی. رخدادهای local که کاربر opt-in نکرده، باید local/no-op باقی بمانند و در dashboard راه دور دیده نشوند.

### ۳.۳. queryهای کنترل کیفیت و dashboard

| view یا query | سؤال پاسخ‌داده‌شده | کنترل پذیرش |
|---|---|---|
| Cohort funnel | چه تعداد install واجد شرایط شدند و چه تعداد به تحلیل معتبر رسیدند؟ | denominator فقط `onboarding_prompt_eligible` یکتا است. |
| Prompt path | کاربر prompt را باز، بعداً انتخاب یا dismiss کرد؟ | مجموع actionها با تعداد eligible قابل توضیح و dedupe‌شده است. |
| Feature path | composition و mass-flow از چه مسیرهایی کامل شدند؟ | `analysis_activation_completed` بدون رخداد محاسبهٔ معتبر صفر است. |
| Time-to-analysis buckets | آیا مسیر در bucketهای `<60s`، `60–180s` یا `>180s` توزیع معنادار دارد؟ | bucketها از پیش ثابت‌اند؛ زمان خام ذخیره/نمایش نمی‌شود. |
| Privacy and integrity | آیا رخداد غیرمجاز یا attribution ناشناخته وجود دارد؟ | نمونهٔ redacted فاقد دادهٔ ممنوع؛ مقدار غیرallow-list صفر است. |
| Error surface | آیا بازکردن تحلیل یا محاسبه، خطای UI ایجاد می‌کند؟ | رخداد خطا فقط `error_code` و `surface` دارد، نه stack trace یا input. |

در گزارش روزانه، تعداد cohort، numerator، error count، unknown attribution، prompt actionها، تعداد گفت‌وگوهای رضایت‌داده‌شده و limitationها درج می‌شود. نرخ‌ها فقط همراه با numerator و denominator منتشر می‌شوند. dashboard نباید رتبه‌بندی کانال، پیش‌بینی CAC یا نتیجه‌گیری آماری را در ترافیک کم نمایش دهد.

## ۴. برنامهٔ روزبه‌روز: روزهای ۱۵ تا ۲۱

### روز ۱۵ — Gate، freeze تعریف‌ها و انتخاب نمونهٔ علمی

| زمان | کار دقیق | مسئول | خروجی | معیار پذیرش |
|---|---|---|---|---|
| ۰۹:۰۰–۱۰:۰۰ | مرور گزارش `CB-W2-MSG-01` و ثبت Go/Hold | Growth Lead + Product Lead | تصمیم مکتوب و لینک evidence | کیفیت attribution و limitationها روشن است. |
| ۱۰:۰۰–۱۱:۰۰ | freeze cohort، metric و allow-list هفتهٔ سوم | Data/Operations + Engineer | `CB-W3-ONB-01` brief | یک ICP، یک workflow و یک metric اصلی دارد. |
| ۱۱:۰۰–۱۲:۰۰ | انتخاب یک مثال آموزشی واقعی از مسیر پشتیبانی‌شدهٔ محصول | Scientific Reviewer + Content | example spec شامل نتیجهٔ مورد انتظار و scope note | formula و نتیجه در هستهٔ محصول آزموده شده‌اند. |
| ۱۳:۰۰–۱۴:۰۰ | تعریف prompt کوتاه و گزینه‌های opt-in | Product + Design | copy و state diagram | dismiss/later بدون تنبیه ممکن است. |
| ۱۴:۰۰–۱۵:۰۰ | privacy/threat review | Engineer + Data | checklist امضاشده | formula و PII در event schema نیستند. |
| ۱۵:۰۰–۱۶:۰۰ | ایجاد flag و rollback plan | Engineer | `onboarding_content_week_3` با default خاموش | خاموش‌کردن flag، مسیر اصلی محصول را تغییر نمی‌دهد. |

**قانون Gate:** اگر هفتهٔ دوم نتیجه‌ای ندارد، تیم حق ندارد variant برنده اعلام کند. `entry_variant` در این حالت `unknown` یا مقدار مستندِ مسیر انتخاب‌شده است و تحلیل فقط exploratory گزارش می‌شود.

### روز ۱۶ — پیاده‌سازی instrumentation و مسیر onboarding

| زمان | کار دقیق | مسئول | خروجی | معیار پذیرش |
|---|---|---|---|---|
| ۰۹:۰۰–۱۰:۳۰ | پیاده‌سازی state machine تحلیل در لایهٔ UI، جدا از هستهٔ شیمی | Desktop Engineer | controller/adapter قابل‌آزمون | منطق `chembalance.py` و `stoichiometry_analysis.py` تغییر نکرده است. |
| ۱۰:۳۰–۱۲:۰۰ | افزودن رخدادهای allow-list و dedupe local | Desktop Engineer | unit tests رخداد | هیچ رخداد حاوی formula یا عدد نتیجه نیست. |
| ۱۳:۰۰–۱۴:۰۰ | اتصال prompt به مسیر `Analysis & charts` | Desktop Engineer + Design | path opt-in | tab و محاسبه به‌صورت واقعی باز می‌شوند. |
| ۱۴:۰۰–۱۵:۰۰ | fallback no-op برای analytics | Engineer | test failure analytics | خرابی analytics، موازنه یا تحلیل را block نمی‌کند. |
| ۱۵:۰۰–۱۶:۰۰ | regression و smoke test headless | QA + Engineer | log تست | tests و UI smoke سبز هستند. |

**پذیرش فنی:** prompt نباید با timer، modal غیرقابل‌بستن یا condition مبهم کاربر را متوقف کند. پیاده‌سازی باید صرفاً نتیجهٔ معتبر موجود را به workspace متصل کند و هیچ فرمولی را برای تحلیل remote serialize نکند.

### روز ۱۷ — asset مسئله‌محور و آماده‌سازی محتوا

| زمان | کار دقیق | مسئول | خروجی | معیار پذیرش |
|---|---|---|---|---|
| ۰۹:۰۰–۱۰:۰۰ | نوشتن outline راهنمای کوتاه | Content + Scientific Reviewer | ساختار «مسئله → موازنه → کنترل → تحلیل → محدودیت» | هر مرحله با UI واقعی قابل‌تکرار است. |
| ۱۰:۰۰–۱۱:۳۰ | تهیهٔ تصویر یا GIF واقعی از build تأییدشده | Design + QA | یک asset تصویری | UI، داده یا capability خیالی ندارد. |
| ۱۱:۳۰–۱۲:۰۰ | نوشتن caption، byline و disclosure روش تولید | Content | نسخهٔ نهایی copy | نویسنده/بازبین و روش استفاده از ابزار روشن است. |
| ۱۳:۰۰–۱۴:۰۰ | افزودن CTA و UTM کنترل‌شده | Web/Content + Engineer | URL registry | فقط یک CTA: «تحلیل مثال را ببین». |
| ۱۴:۰۰–۱۵:۰۰ | accessibility review | Design + QA | alt text و keyboard checks | contrast، focus و scope notice قابل‌دسترسی‌اند. |
| ۱۵:۰۰–۱۶:۰۰ | تأیید علمی/محصول | Scientific Reviewer + Product Lead | sign-off | ادعای feasibility، safety، سرعت یا برتری بی‌پایه حذف شده است. |

این asset باید مسئله‌ای را حل کند که مخاطب شناخته‌شده واقعاً دارد و از عنوان اغراق‌آمیز، تولید انبوه یا محتوای صرفاً برای جذب ترافیک دوری کند.[1] هر آموزش باید تصریح کند که ChemBalance پایستگی ریاضی را کنترل می‌کند، اما امکان‌پذیری شیمیایی، خطرات مواد، شرایط عملیاتی و ایمنی آزمایش را تعیین نمی‌کند.

### روز ۱۸ — اتصال dashboard، QA انتهابه‌انتها و dry run

| زمان | کار دقیق | مسئول | خروجی | معیار پذیرش |
|---|---|---|---|---|
| ۰۹:۰۰–۱۰:۳۰ | ساخت cohort funnel و privacy view | Data/Operations | dashboard v1 هفتهٔ سوم | cohort و eventهای unknown جدا دیده می‌شوند. |
| ۱۰:۳۰–۱۲:۰۰ | اجرای سناریوی prompt-open-composition | QA + Engineer | test record مسیر اول | ترتیب تمام eventها صحیح است. |
| ۱۳:۰۰–۱۴:۰۰ | اجرای سناریوی prompt-dismiss-later-mass-flow | QA + Engineer | test record مسیر دوم | dismiss یک failure یا activation کاذب نمی‌سازد. |
| ۱۴:۰۰–۱۵:۰۰ | negative testing داده | Engineer + Data | privacy test log | invalid token، opt-out و payload غیرمجاز safe fail می‌شوند. |
| ۱۵:۰۰–۱۶:۰۰ | بررسی parity نسخه و asset | Product + QA | release/build matrix | UI تصویر، asset و نسخهٔ قابل‌دریافت هم‌خوان‌اند. |

### روز ۱۹ — توزیع محدود و opt-in

| زمان | کار دقیق | مسئول | خروجی | معیار پذیرش |
|---|---|---|---|---|
| ۰۹:۰۰–۰۹:۴۵ | مرور channel registry و رضایت پیام‌رسانی | Community Lead + Growth Lead | فهرست کوچک کانال‌های مجاز | هیچ فهرست تماس خریداری‌شده یا ارسال انبوه استفاده نمی‌شود. |
| ۰۹:۴۵–۱۱:۰۰ | آماده‌سازی outreach شخصی و مسئله‌محور | Community Lead | پیام‌های فردی با UTM یکتا | هر پیام opt-out و CTA واحد دارد. |
| ۱۱:۰۰–۱۲:۰۰ | انتشار asset در یک کانال مرتبط | Content | URL و timestamp انتشار | مسیر asset تا CTA آزموده شده است. |
| ۱۳:۰۰–۱۴:۰۰ | پایش integrity در اولین cohort | Data/Operations | snapshot روزانه | anomaly به‌جای rate ظاهراً خوب اولویت دارد. |
| ۱۴:۰۰–۱۵:۰۰ | پاسخ‌گویی انسانی به پرسش‌های اولیه | Product/Community | log دسته‌بندی‌شده | هیچ input شیمیایی یا اطلاعات تماس بدون رضایت وارد analytics نمی‌شود. |
| ۱۵:۰۰–۱۶:۰۰ | تصمیم ادامه/مکث توزیع | Growth Lead | decision log | در صورت مشکل داده یا privacy، توزیع فوراً pause می‌شود. |

هفتهٔ سوم هنوز مرحلهٔ توزیع محدود است. paid acquisition، retargeting، قیمت‌گذاری و ادعای رشد تا ورود به مرحلهٔ جداگانه و گذر از Gateهای واقعی در برنامه نیستند.

### روز ۲۰ — مصاحبهٔ کوتاه، observation و triage اصطکاک

| زمان | کار دقیق | مسئول | خروجی | معیار پذیرش |
|---|---|---|---|---|
| ۰۹:۰۰–۱۰:۰۰ | دعوت رضایت‌محور به گفت‌وگوی ۱۵ تا ۲۰ دقیقه‌ای | Product + Community | دعوت‌نامه و فرم رضایت | ضبط، نام و contact اختیاری و جدا از analytics هستند. |
| ۱۰:۰۰–۱۲:۰۰ | مشاهدهٔ اجرای workflow بدون راهنمایی | Product + Scientific Reviewer | یادداشت ساختاریافته | محل توقف، انتظار کاربر و wording ثبت می‌شود؛ نه formula شخصی. |
| ۱۳:۰۰–۱۴:۰۰ | دسته‌بندی feedback و مقایسه با funnel | Data + Product | synthesis board | evidence کمی/کیفی جدا اما پیوندخورده است. |
| ۱۴:۰۰–۱۵:۰۰ | انتخاب یک اصطکاک P0 یا ثبت «evidence ناکافی» | Product + Engineer | triage decision | بیش از یک تغییر محصول هم‌زمان انتخاب نمی‌شود. |
| ۱۵:۰۰–۱۶:۰۰ | رفع محدود یا prototype و regression | Engineer + QA | patch/experiment note | regression و scope علمی کنترل شده‌اند. |

**راهنمای مصاحبه:** «در این صفحه انتظار داری چه کاری انجام دهی؟»، «اولین نتیجهٔ مفید برای تمرین/تدریس تو چیست؟»، «کدام عبارت یا گام نامفهوم بود؟» و «اگر ادامه ندهی، علت اصلی چیست؟». مصاحبه‌گر نباید پاسخ را القا کند، وعدهٔ feature بدهد یا درخواست فرمول، نام، ایمیل یا اطلاعات کلاس را در یادداشت عملیاتی وارد کند.

### روز ۲۱ — مرور evidence، Go/Hold و handoff هفتهٔ چهارم

| زمان | کار دقیق | مسئول | خروجی | معیار پذیرش |
|---|---|---|---|---|
| ۰۹:۰۰–۱۰:۳۰ | مرور dashboard همراه با denominator و sample limitations | Data + Growth | snapshot پایانی | همهٔ نرخ‌ها numerator/denominator دارند. |
| ۱۰:۳۰–۱۱:۳۰ | مرور recording/notes رضایت‌داده‌شده و synthesis | Product + Research Owner | learning memo | quote یا دادهٔ حساس بدون رضایت منتشر نمی‌شود. |
| ۱۳:۰۰–۱۴:۰۰ | بررسی privacy، build و rollback | Engineer + QA | QA/rollback sign-off | failure باز P0 وجود ندارد. |
| ۱۴:۰۰–۱۵:۰۰ | تصمیم Go/Hold/Iterate | Growth Lead + Founder | تصمیم مکتوب | تصمیم فقط از metric اصلی گرفته نشده است. |
| ۱۵:۰۰–۱۶:۰۰ | ایجاد backlog هفتهٔ چهارم | Product + Content + Engineer | حداکثر یک فرضیهٔ اولویت‌دار | هر ticket evidence، owner و acceptance criterion دارد. |

## ۵. بسته‌های کاری فنی و معیار پذیرش

| اولویت | شناسه | بستهٔ کاری | معیار پذیرش |
|---|---|---|---|
| P0 | `GROW-301` | state machine مستقل برای `analysis_activation_completed` | نتیجهٔ تحلیل واقعی شرط completion است و تعریف activation هفتهٔ اول تغییر نمی‌کند. |
| P0 | `GROW-302` | event contract allow-list، dedupe و unit tests | هیچ payload حاوی formula/PII نیست؛ duplicate activation صفر یا مستند است. |
| P0 | `GROW-303` | flag `onboarding_content_week_3` و rollback | flag پیش‌فرض خاموش است و disable آن محصول اصلی را دست‌نخورده نگه می‌دارد. |
| P0 | `GROW-304` | dashboard cohort و queryهای integrity | denominator ثابت، unknown جدا و event-order ناممکن صفر است. |
| P0 | `GROW-305` | مثال و محتوای علمی تأییدشده | همهٔ مراحل با build واقعی بازتولید شده و scope notice دیده می‌شود. |
| P1 | `GROW-306` | prompt قابل‌بستن با مسیر later | keyboard، dismiss، later و entry از navigation آزمون شده‌اند. |
| P1 | `GROW-307` | feedback دسته‌بندی‌شده و opt-in | پاسخ free-text به analytics ارسال نمی‌شود؛ consent قابل لغو است. |
| P1 | `GROW-308` | registry لینک/UTM و asset ID | source، medium، campaign و asset از allow-list می‌آیند. |
| P2 | `GROW-309` | گزارش aggregate export برای review تیم | timestamp، query version و disclosure در خروجی هستند. |

## ۶. RACI و cadence تصمیم‌گیری

| فعالیت | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| فرضیه، Gate و تصمیم هفته | Growth Lead | بنیان‌گذار | Product Lead، Data، Scientific Reviewer | تیم محصول |
| state machine، flag و تست محصول | Desktop Engineer | Product Lead | QA، Data | Growth Lead |
| schema، dashboard و privacy queries | Data/Operations | Growth Lead | Engineer، Product | بنیان‌گذار |
| مثال علمی و scope notice | Scientific Reviewer + Content | Product Lead | Desktop Engineer | Community Lead |
| asset، URL و accessibility | Content/Design | Growth Lead | QA، Scientific Reviewer | تیم محصول |
| outreach محدود و دعوت مصاحبه | Community Lead | Growth Lead | Product | بنیان‌گذار |
| واکنش incident و rollback | Engineer | Product Lead | Data، QA | Growth Lead |

هر روز ساعت ۱۶:۰۰ یک مرور ۱۵ دقیقه‌ای انجام می‌شود: وضعیت build، privacy، integrity رخدادها، feedback، blocker و تصمیم pause/continue. این مرور جایگزین گزارش‌سازی ظاهری نیست و در صورت نبود دادهٔ معتبر، باید صریحاً «not measured» ثبت کند.

## ۷. قواعد UTM، attribution و حفاظت داده

| مورد | قاعدهٔ اجرایی |
|---|---|
| ساختار URL | `utm_source={channel}&utm_medium={format}&utm_campaign=cb_w3_onboarding_content&utm_content={asset_or_prompt}`؛ همه lowercase و از registry. |
| allow-list `utm_content` | `analysis_example`, `teacher_guide`, `prompt_balance_to_analysis`؛ مقدار دیگر به `unknown`. |
| انتقال attribution | فقط token کوتاه، دارای expiry و امضاشده یا mapping build-time؛ نه query کامل، نه referrer خام. |
| رضایت | default برابر `essential_only`؛ ارسال remote تنها با `analytics_opt_in` صریح. |
| حداقل‌سازی | formula، equation، نام species، مقدار جرم/درصد، نام، ایمیل، IP خام، user-agent کامل و fingerprint ممنوع است. |
| نگهداشت | eventهای test پس از QA پاک یا ناشناس‌سازی شوند؛ دورهٔ نگهداشت production پیش از launch در policy مستقل تصویب شود. |
| دسترسی | فقط نقش‌های Product/Data مجاز به aggregate dashboard هستند؛ دسترسی raw نیازمند دلیل و ثبت review است. |

در صورت مشاهدهٔ دادهٔ ممنوع، endpoint/flag فوراً غیرفعال می‌شود، دادهٔ ناسازگار قرنطینه و پاک‌سازی می‌شود، incident owner تعیین می‌گردد و تا رفع ریشه‌ای، هیچ تحلیل یا توزیع جدید انجام نخواهد شد.

## ۸. Go / Hold / Iterate و قواعد گزارش

| تصمیم | شرایط لازم | اقدام بعدی |
|---|---|---|
| Go به آزمایش محدود هفتهٔ چهارم | integrity رخدادها، privacy، build و replay مسیرها معتبرند؛ cohort با تعریف ثابت گزارش شده؛ شواهد کیفی کافی یا علت مستند برای کمبود آن وجود دارد؛ یک اصطکاک اولویت‌دار شناسایی شده است | فقط یک تغییر یا یک مقایسهٔ کنترل‌شدهٔ بعدی را در هفتهٔ چهارم اجرا کنید. |
| Iterate | مسیر معتبر است، اما feedback و funnel به یک مانع روشن در copy، prompt یا navigation اشاره می‌کنند | یک اصلاح محدود با flag، acceptance test و تاریخ review بسازید. |
| Hold | attribution، event order، version parity یا privacy ناسالم است؛ build regression وجود دارد؛ یا cohort تعریف‌نشده است | توزیع را pause، مشکل P0 را رفع، QA را تکرار و baseline را دوباره ثبت کنید. |
| Stop | incident حریم خصوصی، نقض scope علمی، یا failure محصولی که به ایمنی/اعتماد آسیب می‌زند رخ دهد | feature/asset را خاموش یا unpublish، incident review و اطلاع‌رسانی متناسب انجام دهید. |

هیچ درصد موفقیت از پیش تعیین نشده است، زیرا baseline واقعی هنوز ثبت نشده و threshold ساختگی می‌تواند تصمیم را منحرف کند. هر نتیجه باید با تاریخ، version، cohort definition، numerator، denominator، تعداد رخداد `unknown`، تعداد گفتگوهای رضایت‌داده‌شده و محدودیت نمونه گزارش شود.

## ۹. خطرها، rollback و کنترل علمی

| خطر | نشانهٔ زودهنگام | واکنش فوری | rollback |
|---|---|---|---|
| prompt مزاحم یا مبهم | dismiss زیاد یا feedback `navigation` | copy و trigger را بازبینی کنید؛ نتیجه‌گیری از کلیک صرف نکنید | flag را خاموش کنید؛ navigation اصلی باقی می‌ماند. |
| فعال‌سازی کاذب | completion پیش از calculation یا duplicate | state machine و dedupe را متوقف/اصلاح کنید | event ارسال نشود تا tests سبز شوند. |
| نشتی formula/PII | نمونهٔ payload دادهٔ ممنوع دارد | incident privacy، قطع ارسال، پاک‌سازی و review | adapter remote را no-op کنید. |
| ادعای علمی بیش از دامنه | پرسش یا feedback دربارهٔ safety/feasibility | scope notice و asset را همان روز اصلاح کنید | asset را unpublish و prompt را disable کنید. |
| محتوای جدا از مسئلهٔ کاربر | content open زیاد ولی مسیر محصول کامل نمی‌شود | مثال و proof را با گفت‌وگو بازنویسی کنید | توزیع asset را pause کنید. |
| نتیجه‌گیری از نمونهٔ کم | تفاوت ظاهری بدون cohort کافی | گزارش را exploratory بنویسید و sample را گسترش ندهید مگر integrity پایدار باشد | هیچ variant یا بودجه‌ای به‌عنوان برنده ثبت نشود. |

## ۱۰. backlog پیشنهادی هفتهٔ چهارم

backlog فقط پس از تصمیم روز ۲۱ اولویت می‌گیرد. در نبود evidence کافی، همهٔ موارد زیر در وضعیت discovery باقی می‌مانند.

| شرطی که در هفتهٔ سوم دیده می‌شود | فرضیهٔ هفتهٔ چهارم | اقدام محدود پیشنهادی | معیار پذیرش |
|---|---|---|---|
| prompt باز می‌شود اما تحلیل شروع نمی‌شود | wording یا placement مسیر تحلیل واضح نیست | یک copy/placement کنترل‌شده، نه redesign کامل | event order و privacy سالم؛ feedback هدفمند جمع‌آوری شده است. |
| analysis باز می‌شود اما calculation کامل نمی‌شود | مثال یا affordance محاسبه مبهم است | یک quick-start context-aware در همان workspace | simulation/QA هر دو مسیر را کامل می‌کنند. |
| content باعث ورود می‌شود اما first-open کم است | اصطکاک install یا trust مانع است | بهبود راهنمای install یا disclosure signing، بدون تغییر پیام اصلی | مسیر install-to-first-open قابل‌ردیابی و build معتبر است. |
| مصاحبه‌ها نیاز آموزشی متفاوتی نشان می‌دهند | ICP/وظیفهٔ انتخاب‌شده نیاز به refinement دارد | یک discovery study کوچک پیش از feature جدید | تصمیم بر پایهٔ evidence مکتوب، نه حدس تیم. |
| data integrity ناقص است | measurement برای تصمیم کافی نیست | hardening instrumentation | queryهای کنترل کیفیت و privacy پاس می‌شوند. |

## ۱۱. خروجی‌های اجباری پایان هفتهٔ سوم

1. brief امضاشدهٔ `CB-W3-ONB-01` شامل ICP، workflow، CTA، metric، guardrail و rule توقف.
2. state machine و event dictionary هفتهٔ سوم، همراه با unit test، dedupe و allow-list.
3. flag قابل rollback با default امن و runbook قطع مسیر.
4. dashboard cohort همراه با definition، query version، sample limitation و privacy view.
5. یک asset مسئله‌محورِ بازبینی‌شدهٔ علمی، دارای byline، disclosure روش تولید، UTM و CTA واحد.
6. گزارش QA انتهابه‌انتها برای open، dismiss، later، composition، mass-flow، opt-out و failure analytics.
7. synthesis مصاحبه/observation رضایت‌محور یا ثبت صریح دلیل نبود آن.
8. learning memo روز ۲۱ با تصمیم Go/Hold/Iterate و حداکثر یک فرضیهٔ اولویت‌دار برای هفتهٔ چهارم.

## افشای مبنا و محدودیت‌ها

این سند، یک runbook اجرایی برای هفتهٔ سوم کمپین ۹۰روزهٔ ChemBalance است و مبتنی بر وضعیت محصول و اسناد داخلی تا **۲۸ اوت ۲۰۲۶** تنظیم شده است. هیچ دادهٔ واقعی CAC، conversion، retention، درآمد، تعداد نصب یا برتری آماری در این سند ادعا نشده است؛ هر metric تا زمان اندازه‌گیری واقعی **pending** است. ارقام مالی موجود در اسناد Seed ChemBalance، در صورت استفاده، مفروضات مدیریتی‌اند و نباید به traction یا قرارداد واقعی تعبیر شوند.

منطق برنامه بر تمرکز بر ارزش نخست، مشاهدهٔ ریزش‌ها، پژوهش مستمر کاربر و محتوای people-first استوار است.[1] [2] [3] این استراتژی تضمین رشد، جذب سرمایه، conversion یا ایمنی شیمیایی ارائه نمی‌دهد. ChemBalance تنها سازگاری ریاضی موازنه و تحلیل‌های محاسباتی تعریف‌شده را ارائه می‌کند و جایگزین ارزیابی امکان‌پذیری واکنش، اطلاعات ایمنی مواد، رویهٔ آزمایشگاهی یا نظر متخصص نیست.

## منابع

[1]: https://developers.google.com/search/docs/fundamentals/creating-helpful-content "Google Search Central — Creating Helpful, Reliable, People-First Content"

[2]: https://www.userinterviews.com/blog/how-to-design-successful-onboarding-flows-with-ux-research "User Interviews — How to Design Successful Onboarding Flows with UX Research"

[3]: https://www.gainsight.com/blog/customer-onboarding/ "Gainsight — Customer Onboarding: Best Practices and Actionable Tips"

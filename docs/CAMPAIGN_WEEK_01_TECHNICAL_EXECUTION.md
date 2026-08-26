# برنامهٔ اجرایی و وظایف فنی هفتهٔ اول کمپین دیجیتال ChemBalance

**هدف هفته:** ایجاد یک مسیر اندازه‌گیری‌شده و قابل‌اعتماد از صفحهٔ ورود تا فعال‌سازی در محصول؛ بدون خرید تبلیغ، بدون گسترش کانال و بدون ادعای رشد قبل از اطمینان از داده.

**تعریف پایان موفق هفته:** دو کاربر داخلی بتوانند از یک URL دارای UTM وارد مسیر شوند، برنامه را دریافت/اجرا کنند، واکنشی را وارد کنند، موازنه را ببینند، کنترل پایستگی را باز کنند و خروجی را کپی یا export کنند؛ تمام گام‌ها باید با timestamp و منبع در dashboard دیده شوند.

> **قانون هفتهٔ اول:** هیچ هزینهٔ تبلیغاتی، outreach انبوه یا گزارش conversion منتشر نشود مگر آن‌که مسیر رخدادها، حریم خصوصی و کنترل کیفیت داده از این سند عبور کرده باشند.

## ۱. محدودهٔ هفته و موارد خارج از محدوده

| در محدوده | خارج از محدوده |
|---|---|
| event taxonomy، instrumentation حداقلی، landing page اولیه، UTM، dashboard، QA و policy داده | اجرای paid ads، مقیاس‌کردن SEO، برنامهٔ referral، CRM پیچیده، آزمایش قیمت‌گذاری یا جمع‌آوری اطلاعات حساس |
| یک ICP: مدرس/TA شیمی و یک use case: موازنهٔ واکنش یونی یا واکنش پیچیده | شخصی‌سازی هم‌زمان برای آزمایشگاه، ناشر، مدرسه و بازار عمومی |
| یک CTA: «مثال را اجرا کنید / نسخه را دریافت کنید» | چند CTA در یک صفحه یا فرم طولانی lead generation |

## ۲. مالکیت و ظرفیت پیشنهادی

| نقش | مالک | ظرفیت پیشنهادی هفته | خروجی غیرقابل‌واگذاری |
|---|---|---:|---|
| Product/Growth Lead | بنیان‌گذار محصول | ۷–۹ ساعت | تصمیم فرضیه، تعریف metric اصلی، تأیید انتشار و تصمیم Go/No-Go |
| Desktop Engineer | مهندس محصول | ۱۲–۱۶ ساعت | رخدادهای درون‌محصولی، feature flag، خطایابی و build آزمایشی |
| Web/Content Owner | محتوا یا طراح محصول | ۱۰–۱۴ ساعت | landing page، مثال علمی، CTA و UTM linkهای نهایی |
| Data/Operations Owner | محصول یا تحلیلگر | ۶–۸ ساعت | dashboard، data dictionary، کنترل privacy و گزارش baseline |
| Scientific Reviewer | مدرس/مشاور علمی | ۱–۲ ساعت | صحت formula، equation، wording و disclaimer علمی |

اگر یک نفر بیش از یک نقش را دارد، کارهای او به ترتیب «دادهٔ قابل‌اعتماد → مسیر فعال‌سازی → صفحهٔ ورود → زیباسازی» اولویت‌بندی شوند.

## ۳. قرارداد فنی رخدادها

### ۳.۱. شناسه و حریم خصوصی

هر install یک `anonymous_install_id` تصادفی تولید می‌کند. این شناسه نباید از ایمیل، نام، متن واکنش، hardware fingerprint یا شناسهٔ پایدار سیستم ساخته شود. متن معادله به‌صورت پیش‌فرض ارسال نمی‌شود. اگر در آینده برای بررسی خطا نیاز به نمونهٔ equation باشد، باید رضایت جداگانه، ناشناس‌سازی و policy نگهداشت مکتوب اضافه شود.

| فیلد مشترک | نوع | توضیح |
|---|---|---|
| `event_name` | string | نام رخداد از taxonomy کنترل‌شده |
| `event_time_utc` | ISO-8601 | زمان تولید رخداد در UTC |
| `anonymous_install_id` | UUID | شناسهٔ تصادفی محلی، بدون PII |
| `app_version` | string | مانند `1.1.0-dev` |
| `platform` | enum | `windows`، `macos` یا `linux` |
| `source_channel` | enum | `organic`، `direct`، `partner`، `email`، `paid` یا `unknown` |
| `utm_source` / `utm_medium` / `utm_campaign` | string/null | فقط هنگام ورود از URL یا installer link |
| `experiment_id` | string/null | برای A/B یا landing variant |
| `consent_state` | enum | `essential_only` یا `analytics_opt_in` |

### ۳.۲. رخدادهای هفتهٔ اول

| رخداد | trigger دقیق | خصوصیات اختصاصی مجاز | معیار پذیرش |
|---|---|---|---|
| `landing_view` | بازشدن landing page | `page_id`, `variant_id` | با refresh و UTM درست ثبت شود |
| `cta_clicked` | کلیک CTA اصلی | `cta_id`, `destination` | در تمام deviceهای آزمون ثبت شود |
| `installer_started` | آغاز دریافت/اجرای installer یا لینک download | `release_channel` | بدون PII و با attribution منبع ثبت شود |
| `app_first_opened` | اولین اجرای موفق desktop app | `first_run=true` | فقط یک‌بار برای هر install ثبت شود |
| `example_opened` | بارشدن مثال با دکمهٔ نمونه | `example_id` | متن equation ارسال نشود |
| `equation_entered` | متن input از حالت خالی به غیرخالی می‌رود | `character_bucket` اختیاری | متن equation ذخیره/ارسال نشود |
| `equation_balanced` | `balance_equation` با موفقیت `BalanceResult` می‌دهد | `species_count`, `has_charge` | موفقیت محاسبه و نه صرف کلیک ثبت شود |
| `conservation_checked` | جدول کنترل با نتیجهٔ valid نمایش می‌گیرد | `constraint_count` | فقط پس از نتیجهٔ موفق ثبت شود |
| `result_exported` | copy یا export موفق است | `export_kind` (`copy`/`txt`) | صرف بازشدن dialog export ثبت نشود |
| `activation_completed` | چهار گام معیار فعال‌سازی برای یک install کامل می‌شود | `time_to_value_seconds` | فقط یک‌بار برای هر activation cycle |
| `app_error_shown` | خطای قابل‌نمایش در UI | `error_code`, `surface` | بدون stack trace یا equation |

### ۳.۳. شبه‌کد instrumentation

```python
@dataclass(frozen=True)
class AnalyticsEvent:
    event_name: str
    event_time_utc: str
    anonymous_install_id: str
    app_version: str
    platform: str
    properties: dict[str, str | int | bool | None]

class AnalyticsPort(Protocol):
    def track(self, event: AnalyticsEvent) -> None: ...

# در حالت local-first، adapter پیش‌فرض می‌تواند رخداد را در یک صف local
# نگه دارد و فقط در صورت analytics_opt_in آن را ارسال کند.

if result_is_valid:
    analytics.track(event("equation_balanced", species_count=len(result.all_species)))
    analytics.track(event("conservation_checked", constraint_count=len(result.verification)))
```

این interface به `app.py` اجازه می‌دهد یک adapter سادهٔ no-op یا local queue در توسعه داشته باشد و در آینده بدون تغییر در منطق شیمی، provider تحلیلی جدید تزریق شود.

## ۴. برنامهٔ روزبه‌روز

### روز ۱ — تصمیم، طراحی داده و آماده‌سازی محیط

| بازه | کار | مالک | خروجی | معیار پذیرش |
|---|---|---|---|---|
| ۰۹:۰۰–۰۹:۳۰ | kick-off و مرور هدف هفته | Product/Growth Lead | یک صفحهٔ تصمیم با ICP، use case، CTA و metric اصلی | همهٔ نقش‌ها می‌دانند «activation» چیست |
| ۰۹:۳۰–۱۱:۰۰ | نوشتن data dictionary و naming convention | Data/Operations + Engineer | جدول رخدادها، properties و privacy constraints | هر رخداد trigger و مالک دارد |
| ۱۱:۰۰–۱۲:۰۰ | threat/privacy review سبک | Product + Engineer | فهرست داده‌های ممنوع و retention draft | equation، PII و fingerprint از scope حذف شده‌اند |
| ۱۳:۰۰–۱۵:۰۰ | انتخاب یا ساخت AnalyticsPort | Engineer | interface، adapter توسعه و feature flag | app با provider خام یا کلید در source ساخته نمی‌شود |
| ۱۵:۰۰–۱۶:۰۰ | آماده‌سازی محیط QA | Engineer + Data | دو install آزمایشی، test URL، event sink | هر install شناسهٔ متفاوت و ناشناس دارد |
| ۱۶:۰۰–۱۶:۳۰ | مرور پایان روز | همهٔ مالک‌ها | backlog روز ۲ | blocking issueها مالک و زمان دارند |

**کار فنی روز ۱:** یک فایل `analytics.py` یا adapter جدا از `app.py` بسازید. کلید provider یا URL حساس هرگز hard-code نشود؛ configuration از environment یا تنظیمات build بیاید. در حالت پیش‌فرض، `analytics_opt_in=False` باشد تا local-first بودن محصول نقض نشود.

### روز ۲ — اتصال رخدادهای محصول و آزمون واحد

| بازه | کار | مالک | خروجی | معیار پذیرش |
|---|---|---|---|---|
| ۰۹:۰۰–۱۱:۰۰ | افزودن `app_first_opened` و `example_opened` | Engineer | رخدادهای lifecycle اولیه | هر رخداد در log توسعه دیده شود |
| ۱۱:۰۰–۱۳:۰۰ | افزودن رخدادهای balance و validation | Engineer | `equation_entered`, `equation_balanced`, `app_error_shown` | outcome واقعی محاسبه ثبت شود، نه کلیک button |
| ۱۴:۰۰–۱۵:۳۰ | افزودن `conservation_checked` و `result_exported` | Engineer | رخدادهای value proof | copy و export موفق به‌صورت متمایز ثبت شوند |
| ۱۵:۳۰–۱۷:۰۰ | unit test برای dedupe و privacy | Engineer | تست‌های automation | هیچ payload حاوی equation یا PII نیست |

**جزئیات پیاده‌سازی:** رخداد `equation_entered` باید debounce شود تا با هر keystroke ایجاد نشود؛ یک رخداد در اولین تغییر از empty به non-empty در هر session کافی است. `activation_completed` در یک state machine محلی ساخته شود: `balanced → verification_displayed → exported`; اگر کاربر عقب برگردد یا خطا دهد، cycle دوباره از ابتدا شروع نمی‌شود مگر آن‌که یک equation جدید موازنه کند.

### روز ۳ — landing page، UTM و attribution

| بازه | کار | مالک | خروجی | معیار پذیرش |
|---|---|---|---|---|
| ۰۹:۰۰–۱۰:۳۰ | نوشتن پیام landing page | Content + Product | headline، proof، scope notice و CTA | فقط یک CTA اصلی و یک مسئلهٔ مشخص |
| ۱۰:۳۰–۱۲:۰۰ | افزودن مثال علمی و اسکرین‌شات | Content + Scientific Reviewer | صفحهٔ مثال موازنهٔ یونی یا hydrate | formula و disclaimer تأیید شده‌اند |
| ۱۳:۰۰–۱۴:۳۰ | پیاده‌سازی UTM parser و link generator | Web/Engineer | convention و لینک‌های تست | source/medium/campaign در click و download حفظ می‌شود |
| ۱۴:۳۰–۱۶:۰۰ | eventهای `landing_view` و `cta_clicked` | Web/Engineer | event payload و dashboard feed | variant/page id و UTM قابل‌مشاهده‌اند |
| ۱۶:۰۰–۱۶:۳۰ | mobile/desktop QA | Design + QA | screenshot و bug list | CTA، contrast و scope notice قابل‌خواندن‌اند |

**قالب UTM اجباری:** `utm_source={channel}&utm_medium={format}&utm_campaign=cb_w1_activation&utm_content={asset_or_variant}`. نام‌ها lowercase، بدون فاصله و با underscore هستند. هیچ لینک ناشناسی وارد outreach یا social post نمی‌شود.

### روز ۴ — dashboard و کنترل کیفیت funnel

| بازه | کار | مالک | خروجی | معیار پذیرش |
|---|---|---|---|---|
| ۰۹:۰۰–۱۰:۳۰ | ساخت نمودار funnel | Data/Operations | dashboard v1 | از landing تا activation قابل‌فیلتر است |
| ۱۰:۳۰–۱۲:۰۰ | ساخت view زمان تا ارزش | Data/Operations | distribution `time_to_value_seconds` | outlier و رخداد ناقص قابل‌شناسایی‌اند |
| ۱۳:۰۰–۱۴:۰۰ | ساخت view خطا | Data + Engineer | error dashboard با code/surface | بدون پیام کاربر یا equation |
| ۱۴:۰۰–۱۵:۳۰ | تعریف query کنترل داده | Data | QA checklist query | تناقض‌های event order را پیدا می‌کند |
| ۱۵:۳۰–۱۷:۰۰ | dry run کامل | همه | runbook تکمیل‌شده | funnel برای دو install داخلی یکسان و قابل‌توضیح است |

**کنترل‌های لازم:** برای هر `activation_completed` باید قبل از آن `equation_balanced` و `conservation_checked` باشد. `result_exported` بدون equation موفق باید صفر باشد. `app_first_opened` در یک install بیش از یک‌بار نباید وجود داشته باشد. UTM تهی برای test URL یک bug attribution است.

### روز ۵ — آزمون کاربر داخلی و بازبینی تجربه

| بازه | کار | مالک | خروجی | معیار پذیرش |
|---|---|---|---|---|
| ۰۹:۰۰–۱۰:۰۰ | تعریف سناریوی test | Product + Scientific Reviewer | script سه‌مرحله‌ای تست | شامل مثال ساده، یونی و یک خطای input است |
| ۱۰:۰۰–۱۲:۰۰ | تست با دو کاربر داخلی خارج از تیم توسعه | Product | observation notes | کاربر بدون راهنمای شفاهی مسیر را طی می‌کند |
| ۱۳:۰۰–۱۴:۳۰ | replay داده و مصاحبهٔ کوتاه | Data + Product | gap list | هر ریزش با data و quote ثبت می‌شود |
| ۱۴:۳۰–۱۶:۰۰ | اصلاح quick-start و پیام خطا | Engineer + Content | build آزمایشی جدید | خطای اصلی یا ابهام اصلی کاهش یافته است |
| ۱۶:۰۰–۱۶:۳۰ | تصمیم انتشار محدود | Product/Growth Lead | Go / Hold / Fix decision | معیارهای بخش ۵ ارزیابی شده‌اند |

### روز ۶ — hardening، مستندسازی و release candidate

| بازه | کار | مالک | خروجی | معیار پذیرش |
|---|---|---|---|---|
| ۰۹:۰۰–۱۰:۳۰ | regression test و privacy review نهایی | Engineer | گزارش آزمون و code review | تست‌ها سبز و payloadها کنترل شده‌اند |
| ۱۰:۳۰–۱۲:۰۰ | نوشتن runbook پاسخ به خطا | Engineer + Operations | troubleshooting guide | مالک، severity و مسیر rollback روشن است |
| ۱۳:۰۰–۱۴:۳۰ | آماده‌سازی نسخهٔ محدود landing/page | Web + Content | URL نهایی و asset list | همهٔ لینک‌ها UTM صحیح دارند |
| ۱۴:۳۰–۱۶:۰۰ | ساخت release candidate | Engineer | artifact دارای version | build از CI عبور کرده یا قابل‌تکرار است |
| ۱۶:۰۰–۱۶:۳۰ | handoff به هفتهٔ ۲ | همه | backlog اولویت‌دار | فقط یک فرضیهٔ اصلی هفتهٔ بعد تعیین شده است |

### روز ۷ — مرور مدیریتی و سکون عملیاتی

روز ۷ برای هزینه‌کرد، توسعهٔ feature یا انتشار جدید استفاده نمی‌شود. مالک رشد یک گزارش یک‌صفحه‌ای می‌سازد: چه چیزی آماده شد، چه چیزی هنوز اندازه‌گیری نمی‌شود، چه ریسک‌هایی باقی مانده‌اند و هفتهٔ ۲ چه تصمیمی را خواهد آزمود. این سکون کوتاه از شروع هم‌زمان چند آزمایش بدون مبنا جلوگیری می‌کند.

## ۵. معیار Go / Hold برای ورود به هفتهٔ دوم

| معیار | Go | Hold / Fix |
|---|---|---|
| مسیر رخداد | همهٔ رخدادهای activation با ترتیب درست ثبت می‌شوند | رخداد مفقود، تکراری یا ترتیب ناممکن دارد |
| حریم خصوصی | payload نمونه فاقد PII و متن equation است | دادهٔ حساس یا کلید provider در client دیده می‌شود |
| attribution | UTM از page تا first-open یا install قابل‌ردیابی است | منبع ورود گم می‌شود یا فقط direct دیده می‌شود |
| تجربه | دو کاربر داخلی activation را بدون کمک کامل می‌کنند | user بدون کمک در install، مثال یا control گیر می‌کند |
| محتوا | example و scope notice توسط بازبین علمی تأیید شده‌اند | formula، ادعا یا disclaimer مبهم است |
| کیفیت build | آزمون‌های هسته و smoke test موفق‌اند | failure یا regression شناخته‌شده باز است |

## ۶. backlog فنی آماده برای هفتهٔ دوم

| اولویت | کار | دلیل |
|---|---|---|
| P0 | رفع هر خطای instrumentation یا privacy | بدون دادهٔ سالم، هیچ نتیجهٔ رشد معتبر نیست |
| P0 | اصلاح بزرگ‌ترین ریزش در quick-start | فعال‌سازی پیش‌نیاز همهٔ کانال‌هاست |
| P1 | افزوده‌شدن مثال دوم نقش‌محور | تست بازگشت و استفادهٔ تکراری |
| P1 | trigger پیام برای نصب بدون ورود واکنش | کوتاه‌کردن time-to-first-value |
| P2 | feature flag برای landing variant | A/B کنترل‌شده بدون branch محصول |
| P2 | export privacy-safe diagnostic bundle با opt-in | کمک به رفع خطا بدون ذخیرهٔ formula پیش‌فرض |

## ۷. خطرها و واکنش فوری

| خطر | نشانهٔ زودهنگام | واکنش فوری |
|---|---|---|
| دادهٔ نادرست | تعداد activation از balance بیشتر است | توقف تصمیم رشد، بررسی trigger و query کنترل |
| نقض local-first | equation یا PII در log/analytics دیده می‌شود | ارسال را قطع، داده را پاک و policy را بازبینی کنید |
| پیچیدگی بیش از حد | dashboard یا CRM مانع release می‌شود | به event sink و dashboard حداقلی برگردید |
| پیام مبهم | کاربر CTA را می‌بیند اما demo شروع نمی‌کند | headline و مثال اول را تغییر دهید، نه حجم محتوا را |
| اصطکاک نصب | first-open نسبت به download پایین است | راهنمای نصب، signing و build pipeline را اولویت دهید |
| scope علمی مبهم | کاربر دربارهٔ safety/feasibility برداشت نادرست دارد | disclaimer را در صفحه، app و export برجسته کنید |

## ۸. خروجی‌های اجباری هفتهٔ اول

1. `event_dictionary_v1.md` با رخدادها، triggerها و payloadهای مجاز.
2. landing page با یک مسئله، یک CTA، مثال معتبر، UTM و scope notice.
3. adapter تحلیلی opt-in یا local queue که به هستهٔ شیمی وابسته نیست.
4. dashboard funnel و query کنترل کیفیت داده.
5. گزارش QA دو کاربر داخلی با یافته، owner و اولویت.
6. release candidate یا دستور build تکرارپذیر.
7. گزارش Go/Hold یک‌صفحه‌ای برای هفتهٔ دوم.

## افشای مبنا و محدودیت‌ها

این برنامه، هفتهٔ نخست نقشهٔ ۹۰روزهٔ ChemBalance را به وظایف فنی روزانه تبدیل می‌کند. هیچ CAC، conversion یا retention واقعی مفروض نشده است؛ ابتدا baseline داخلی و سپس رفتار کاربر واقعی اندازه‌گیری خواهد شد. طراحی telemetry بر اصل local-first و حداقل‌سازی داده استوار است و محتوای equation را به‌صورت پیش‌فرض ارسال نمی‌کند. این سند یک runbook عملیاتی است، نه تضمین عملکرد بازاریابی.

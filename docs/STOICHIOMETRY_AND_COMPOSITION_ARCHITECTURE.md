# معماری فنی ماژول‌های تحلیل درصدی عناصر و نمودارهای استوکیومتری

**وضعیت سند:** طراحی اجرایی برای نسخهٔ بعدی ChemBalance Desktop
**هدف:** افزودن تحلیل علمی و تصویرسازی بدون تکرار منطق شیمی در UI، بدون وابستگی شبکه و بدون تبدیل نمودار به منبع حقیقت محاسباتی.

## ۱. نقطهٔ شروع فنی

هستهٔ فعلی ChemBalance از parser فرمول، `Species`، `BalanceResult` و حل دقیق فضای تهی با `Fraction` استفاده می‌کند. در نتیجه، ضرایب موازنه‌شده با حساب ممیز شناور تولید نمی‌شوند و خروجی قابل‌تکرار است.[1] رابط PySide6 نیز نتیجهٔ موازنه را در `current_result` نگه می‌دارد و جدول‌های پایستگی و جرم مولی را از همین مدل پر می‌کند.[2]

ماژول نمونهٔ فعلی، یک prototype مناسب برای لایهٔ محاسبه است: ترکیب درصدی را با `Decimal` محاسبه می‌کند، تبدیل جرم‌به‌جرم را از `BalanceResult` می‌سازد و rendererهای مستقل از UI برای PNG دارد.[3] معماری نسخهٔ محصول باید این prototype را از دایرکتوری مثال خارج کند، قراردادهای داده‌ای پایدار تعریف کند و مرز بین محاسبه، chart specification و widget را روشن نگه دارد.

> **قانون معماری:** هستهٔ شیمی نتیجهٔ مرجع را تولید می‌کند؛ لایهٔ تحلیل فقط آن نتیجه را مصرف می‌کند؛ renderer فقط مدل تحلیل را تصویر می‌کند. هیچ widget، نمودار یا رشتهٔ نمایشی نباید منبع محاسبهٔ علمی باشد.

## ۲. معماری لایه‌ای هدف

```text
User input / saved workspace
          │
          ▼
┌───────────────────────────┐
│ chembalance.py            │  parser + exact balance + Species/BalanceResult
│ exact rational arithmetic │
└─────────────┬─────────────┘
              │ immutable BalanceResult / Species
              ▼
┌─────────────────────────────────────────────┐
│ chembalance_analysis/                       │
│  composition.py  stoichiometry.py limits.py │  pure Decimal-domain services
│  models.py       validation.py               │  immutable analysis models
└─────────────┬───────────────────────────────┘
              │ AnalysisResult + diagnostics
              ├──────────────────────────────┐
              ▼                              ▼
┌─────────────────────────┐       ┌─────────────────────────┐
│ chart_specs.py           │       │ export_service.py       │
│ semantic chart contract  │       │ CSV / JSON / PNG / PDF  │
└─────────────┬───────────┘       └─────────────┬───────────┘
              ▼                                 │
┌─────────────────────────┐                     │
│ Qt chart adapters        │                     │
│ QChart / Matplotlib      │                     │
│ view-only rendering      │                     │
└─────────────┬───────────┘                     │
              ▼                                 ▼
     PySide6 Workspace page          local user-selected export path
```

### وابستگی مجاز

| لایه | مجاز است به چه چیزی وابسته باشد؟ | نباید به چه چیزی وابسته باشد؟ |
|---|---|---|
| `chembalance.py` | کتابخانهٔ استاندارد پایتون | Qt، Matplotlib، فایل UI یا اینترنت |
| `chembalance_analysis` | هستهٔ شیمی، `Decimal` و dataclass | widget، مسیر فایل، theme و clipboard |
| `chart_specs` | مدل‌های تحلیل و قرارداد رنگ/label | محاسبهٔ مستقل درصد یا ضرایب |
| Qt adapter | chart specification و theme | parser داخلی یا فرمول‌های علمی تکراری |
| export service | مدل تحلیل و renderer headless | state پنهان UI یا مسیر ثابت کاربر |

## ۳. ساختار پیشنهادی پوشه‌ها

```text
chembalance_analysis/
├── __init__.py
├── models.py                 # dataclassهای immutable و enumها
├── composition.py            # ترکیب درصدی و جرم مولی Decimal
├── stoichiometry.py          # تبدیل‌های مول، جرم و نسبت ضریب‌ها
├── limiting_reagent.py       # reactant limiting / excess و yield
├── validation.py             # ورودی، واحد و خطاهای domain
├── chart_specs.py            # ChartSpecهای مستقل از renderer
├── export_service.py         # CSV/JSON و درخواست export نمودار
└── tests/
    ├── test_composition.py
    ├── test_stoichiometry.py
    ├── test_limiting_reagent.py
    ├── test_chart_specs.py
    └── test_exports.py

ui/
├── analysis_workspace.py     # صفحهٔ Qt و binding به service
├── analysis_viewmodels.py    # state و commandهای UI
└── chart_widgets.py          # adapterهای Qt یا QGraphicsView
```

این جداسازی به‌جای افزودن توابع بیشتر به `app.py`، امکان اجرای کامل تحلیل در CI بدون نمایش window، تولید report خارج از GUI و توسعهٔ نسخه‌های آینده را فراهم می‌کند.

## ۴. قراردادهای داده‌ای اصلی

تمام مقادیر علمی نمایش‌داده‌شده با `Decimal` حمل می‌شوند. تبدیل به `float` فقط در لبهٔ renderer انجام می‌گیرد، زیرا اغلب کتابخانه‌های نمودار `float` می‌خواهند. محاسبهٔ دقیق ضرایب کماکان در هسته با `Fraction` باقی می‌ماند؛ `Decimal` برای نمایش جرم، درصد و round کردن کنترل‌شده مناسب است.

```python
@dataclass(frozen=True)
class ElementContribution:
    element: str
    atom_count: int
    atomic_weight_g_mol: Decimal
    contribution_g_mol: Decimal
    mass_percent: Decimal

@dataclass(frozen=True)
class CompositionAnalysis:
    species: Species
    molar_mass_g_mol: Decimal
    elements: tuple[ElementContribution, ...]
    displayed_percent_total: Decimal
    rounding_tolerance: Decimal

@dataclass(frozen=True)
class Quantity:
    value: Decimal
    unit: Literal["g", "kg", "mg", "mol", "mmol"]

@dataclass(frozen=True)
class StoichiometryStep:
    label: str
    input_quantity: Quantity
    output_quantity: Quantity
    formula: str

@dataclass(frozen=True)
class StoichiometryAnalysis:
    balanced_result: BalanceResult
    source: Species
    target: Species
    source_coefficient: int
    target_coefficient: int
    steps: tuple[StoichiometryStep, ...]
    final_quantity: Quantity

@dataclass(frozen=True)
class ChartSpec:
    kind: Literal["composition_bar", "mole_ratio_bar", "mass_flow", "yield_waterfall"]
    title: str
    categories: tuple[str, ...]
    series: tuple[ChartSeries, ...]
    annotations: tuple[str, ...]
    source_summary: str
```

### اصل immutability و provenance

هر `AnalysisResult` باید متن ورودی، equation موازنه‌شده، نسخهٔ جدول وزن اتمی، واحدها، policy گردکردن و زمان تولید export را نگه دارد. در نتیجه، کاربر می‌تواند بفهمد نمودار دقیقاً از کدام واکنش، کدام ماده و کدام فرض محاسباتی ایجاد شده است. عنوان نمودار به‌تنهایی برای audit کافی نیست.

## ۵. ماژول ترکیب درصدی عناصر

### ۵.۱. ورودی و خروجی

**ورودی:** یک formula قابل‌پارس مانند `CuSO4·5H2O`، `Ca3(PO4)2` یا `[Fe(CN)6]^3-`.
**خروجی:** جرم مولی، count هر عنصر، سهم جرمی هر عنصر، درصد جرمی، کنترل مجموع درصدها و یک `ChartSpec` میله‌ای افقی.

پارسر موجود hydrates، گروه‌های تو‌در‌تو، یون‌ها و زیرنویس Unicode را در یک نقطه کنترل می‌کند؛ تحلیل composition باید صرفاً `parse_species()` را فراخوانی کند و parser دوم نسازد.[1]

### ۵.۲. فرمول‌ها

برای عنصر `i` با شمار اتم `nᵢ` و وزن اتمی `Aᵢ`:

```text
contributionᵢ (g/mol) = nᵢ × Aᵢ
molar_mass (g/mol)    = Σ contributionᵢ
mass_percentᵢ         = 100 × contributionᵢ / molar_mass
```

گردکردن فقط در لایهٔ نمایش انجام می‌شود. مجموع درصدهای نمایش‌داده‌شده باید با tolerance مشخص، مثلاً `±0.01%`، با ۱۰۰ برابر باشد. اگر به علت گردکردن اختلاف وجود دارد، UI باید «به علت گردکردن» را نمایش دهد، نه این‌که یکی از عناصر را بی‌دلیل اصلاح کند.

### ۵.۳. API پیشنهادی

```python
def analyze_elemental_composition(
    formula: str,
    *,
    display_places: int = 3,
    atomic_weights: Mapping[str, Decimal] | None = None,
) -> CompositionAnalysis:
    ...

def make_composition_chart(analysis: CompositionAnalysis) -> ChartSpec:
    ...
```

`atomic_weights` اختیاری است تا نسخه‌های آینده بتوانند جدول وزن اتمی یا convention آموزشی دیگری را تزریق کنند، اما UI در نسخهٔ اول این گزینه را افشا نمی‌کند. هر تغییر جدول باید در export ثبت شود.

## ۶. ماژول استوکیومتری

### ۶.۱. زنجیرهٔ محاسبه

هر تبدیل باید در گام‌های آشکار نمایش داده شود تا کاربر بتواند نتیجه را بازسازی کند:

```text
جرم منبع → مول منبع → نسبت ضرایب موازنه‌شده → مول هدف → جرم هدف
```

برای تبدیل جرم منبع `mₛ` به جرم هدف `mₜ`:

```text
nₛ = mₛ / Mₛ
nₜ = nₛ × coefficientₜ / coefficientₛ
mₜ = nₜ × Mₜ
```

هستهٔ موازنه تنها مرجع `coefficientₛ` و `coefficientₜ` است. API باید مادهٔ منبع و هدف را با identity کامل (`formula` + `charge`) از `BalanceResult.all_species` انتخاب کند تا واکنش‌های یونی یا species تکراری به اشتباه match نشوند.

### ۶.۲. انواع تبدیل در MVP

| قابلیت | ورودی | خروجی | نمودار مناسب | دامنه / محدودیت |
|---|---|---|---|---|
| جرم → جرم | جرم منبع، species منبع/هدف | جرم هدف | mass-flow bar | منبع باید basis مشخص یا limiting باشد |
| مول → مول | مول منبع، species منبع/هدف | مول هدف | mole-ratio bar | بر نسبت ضرایب صحیح تکیه دارد |
| جرم → مول | جرم منبع و species هدف | مول هدف | step diagram | همان نسبت استوکیومتری |
| مول → جرم | مول منبع و species هدف | جرم هدف | step diagram | همان نسبت استوکیومتری |
| ترکیب درصدی | formula واحد | درصد هر عنصر | composition bar | equation لازم نیست |

### ۶.۳. واکنش‌دهندهٔ محدودکننده و بازده — مرحلهٔ بعدی

این ماژول باید بعد از تثبیت تبدیل‌های پایه اضافه شود. برای هر reactant داده‌شده:

```text
available_molesᵢ = massᵢ / molar_massᵢ
reaction_extentᵢ = available_molesᵢ / coefficientᵢ
limiting_reagent = argmin(reaction_extentᵢ)
```

extent واکنش، مقدار theoretical هر product را تعیین می‌کند. API باید reactantهای missing، جرم صفر/منفی، species خارج از سمت reactant و inputهای تکراری را با خطای domain روشن رد کند. بازده درصدی تنها زمانی محاسبه می‌شود که actual yield و theoretical yield دارای واحد سازگار باشند:

```text
percent_yield = 100 × actual_yield / theoretical_yield
```

## ۷. لایهٔ ChartSpec و renderer

### ۷.۱. چرا ChartSpec مستقل؟

Matplotlib برای PNG headless و تست CI مناسب است، اما embedding مستقیم figure در UI، lifecycle و theme را با منطق علمی مخلوط می‌کند. `ChartSpec` یک قرارداد semantic است: categories، series، units، annotation، caption و source summary. سپس rendererهای مختلف می‌توانند همان spec را رسم کنند.

| renderer | کاربرد | محدودیت |
|---|---|---|
| Matplotlib / Agg | export PNG، CI و مستندات | تعامل کاربر محدود |
| QtCharts یا QGraphicsView adapter | hover، tooltip و resize در Desktop | نباید محاسبه انجام دهد |
| CSV/JSON exporter | audit، استفاده در spreadsheet یا report | chart تولید نمی‌کند |

### ۷.۲. سیاست نمودار

نمودار composition افقی است، زیرا نام element و سهم جرمی را خوانا نگه می‌دارد. نمودار نسبت مولی ستونی با تفکیک رنگ reactant/product است. نمودار mass-flow فقط دو یا چند گام را نشان می‌دهد و زیر آن equation، نسبت مولی و unit چاپ می‌شود. هر نمودار باید caption ثابت زیر را حمل کند:

> «مقادیر از واکنش موازنه‌شده و وزن‌های اتمی نمایش‌داده‌شده محاسبه شده‌اند؛ موازنهٔ ریاضی، امکان‌سنجی یا ایمنی واکنش را تأیید نمی‌کند.»

به دلیل استفاده از رنگ، label عددی و نشانهٔ متنی نیز لازم است تا نمودار برای نمایش تک‌رنگ و کاربر دارای اختلال بینایی قابل‌فهم باشد.

## ۸. اتصال به UI PySide6

### ۸.۱. صفحه و state

یک navigation item جدید با نام **Analysis & charts** به `QStackedWidget` افزوده می‌شود. این صفحه نباید `equation_input` مستقل داشته باشد؛ از `current_result` workspace استفاده می‌کند، اما یک formula-only mode برای analysis درصد جرمی نیز دارد. ViewModel، state زیر را نگه می‌دارد:

```text
current_balance_result
selected_source_species
selected_target_species
input_quantity + unit
analysis_mode
analysis_result
chart_spec
validation_messages
export_state
```

پس از کلیک Balance، `current_result` به viewmodel تزریق و dropdown species با `all_species` پر می‌شود. تغییر source/target یا quantity، service را دوباره فراخوانی می‌کند و هرگز coefficient را از متن label استخراج نمی‌کند.

### ۸.۲. responsive و کارایی

محاسبهٔ composition و تبدیل‌های پایه معمولاً کوتاه‌اند؛ با این حال API باید pure و بدون side effect باشد. render با debounce حدود ۱۵۰–۲۵۰ms پس از تغییر text اجرا شود. برای نمودارهای بزرگ یا export PNG، یک `QThreadPool`/worker فقط `ChartSpec` یا bytes تولید می‌کند و تغییر widget تنها در main Qt thread انجام می‌شود. نتیجهٔ worker باید با request-id مقایسه شود تا پاسخ قدیمی صفحه را بازنویسی نکند.

### ۸.۳. export

کاربر مسیر فایل را انتخاب می‌کند. export شامل سه artifact هماهنگ است: تصویر نمودار، CSV داده‌های زیرین و فایل متنی/JSON دارای equation، species، واحدها، زمان، نسخهٔ app و disclaimer. اگر نوشتن فایل ناموفق شود، UI پیام قابل‌فهم می‌دهد و analysis state را حذف نمی‌کند.

## ۹. مدیریت خطا و صحت علمی

| حالت | رفتار service | رفتار UI |
|---|---|---|
| فرمول نامعتبر | `ChemBalanceError` با مکان خطا | پیام نزدیک ورودی و حفظ متن کاربر |
| equation موازنه‌نشده | تحلیل اجرا نمی‌شود | درخواست اجرای Balance پیش از analysis |
| species انتخابی خارج از equation | خطای domain مشخص | dropdown را به گزینه‌های معتبر محدود کند |
| جرم صفر یا منفی | خطای validation | input قرمز و نمایش واحد مورد انتظار |
| واحد ناسازگار | خطای conversion | پیشنهاد واحدهای مجاز همان نوع quantity |
| درصد نمایش‌داده‌شده خارج tolerance | diagnostic failure | نمودار export نشود؛ خطا ثبت و بررسی شود |
| محدودکننده مبهم | همهٔ reactantها را به کاربر نشان دهد | هشدار tie و نمایش extentها |

هیچ خطای غیرمنتظره نباید raw traceback را به کاربر نشان دهد. UI یک پیام قابل‌عمل می‌دهد؛ telemetry محلی/اختیاری می‌تواند code خطا و نسخه را ثبت کند، بدون ارسال formula یا دادهٔ حساس به‌صورت پیش‌فرض.

## ۱۰. تست و کنترل کیفیت

| لایه | نوع تست | نمونه |
|---|---|---|
| parser integration | unit / regression | `CuSO4·5H2O`، گروه‌های nested، یون‌های با charge |
| composition | exact-domain | مجموع درصدها در tolerance؛ contributionها برابر جرم مولی |
| stoichiometry | golden calculation | `H2 + O2 -> H2O`، تبدیل جرم‌به‌جرم و نسبت ضرایب |
| limiting reagent | boundary | reactant اضافی، tie، zero mass، species نامعتبر |
| chart spec | deterministic snapshot | category، series، label، unit و caption درست |
| renderer | headless PNG smoke | فایل non-empty و بدون exception با `Agg` |
| Qt adapter | smoke / integration | تغییر selection نمودار و جدول را به‌روز می‌کند |
| export | round-trip | CSV شامل دادهٔ نمودار و metadata هماهنگ است |

مرجع نمونهٔ فعلی به‌درستی headless renderer و کنترل مجموع درصد را نشان می‌دهد.[3] نسخهٔ محصول باید آزمون‌های آن را به زیرماژول دائمی منتقل کند و برای هر bug محاسباتی یک regression test اضافه نماید.

## ۱۱. ترتیب پیاده‌سازی پیشنهادی

| increment | دامنه | شرط پذیرش |
|---|---|---|
| ۱ | انتقال pure composition service و مدل‌های immutable | فرمول‌های پیچیده و hydrateها؛ مجموع درصد در tolerance |
| ۲ | ChartSpec و export PNG/CSV headless | نمودار composition و data export قابل‌بازسازی |
| ۳ | جرم→جرم و مول→مول با step table | equation، coefficient و unit در هر گام قابل‌مشاهده |
| ۴ | صفحهٔ Analysis در PySide6 | انتخاب species، ورودی quantity، جدول/نمودار و خطای قابل‌عمل |
| ۵ | limiting reagent، theoretical yield و percent yield | خطاهای boundary و export provenance پوشش داده شده‌اند |
| ۶ | بهینه‌سازی UX و پشتیبانی حرفه‌ای | debounce، accessibility، theme، report template و telemetry opt-in |

## ۱۲. مرزهای مسئولیت محصول

ماژول‌ها تحلیل ریاضی بر پایهٔ فرمول، وزن اتمی و واکنش موازنه‌شده ارائه می‌کنند. آن‌ها دما، فشار، خلوص، side reaction، kinetic limitation، hazard، compatibility یا feasibility واکنش را مدل نمی‌کنند. این محدودیت باید در صفحهٔ analysis، export و راهنمای کاربر تکرار شود.

## منابع

[1]: https://github.com/Ali-Marandi/chembalance/blob/main/chembalance.py "ChemBalance core — parser, Species and exact rational balancing"
[2]: https://github.com/Ali-Marandi/chembalance/blob/main/app.py "ChemBalance Desktop — current PySide6 workspace and result state"
[3]: https://github.com/Ali-Marandi/chembalance/blob/main/examples/stoichiometry_charts.py "ChemBalance — existing composition and stoichiometry chart prototype"

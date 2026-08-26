# نقشهٔ نسخهٔ بعدی ChemBalance و راهنمای CI/CD چندسکویی

## جمع‌بندی اجرایی

**بله، هر دو قابلیت پیشنهادی برای نسخهٔ بعدی کاملاً مناسب‌اند** و با معماری فعلی سازگار هستند. موتور ChemBalance هم‌اکنون فرمول هر گونه، شمارش اتم‌ها، جرم مولی و ضرایب موازنه را به‌صورت ساخت‌یافته در اختیار دارد؛ بنابراین محاسبات درصد جرمی و تحلیل استوکیومتری، توسعهٔ طبیعی همین هسته محسوب می‌شوند. پیشنهاد من عرضهٔ آن‌ها در یک نسخهٔ `v1.1.0` با نام تجاری **Stoichiometry Workspace** است.

محاسبات استوکیومتری زمانی برای کاربر ارزش عملی ایجاد می‌کنند که به واکنش موازنه‌شده متصل باشند: کاربر مقدار شناخته‌شده را با واحد جرم یا مول وارد می‌کند، ChemBalance تبدیل مولی و جرم را نشان می‌دهد، و در مرحلهٔ بعد داده را به نمودار و گزارش قابل‌خروجی تبدیل می‌کند. چنین جریانی با الگوی ابزارهای آموزشی و محاسباتی موجود نیز هم‌راستاست؛ برای مثال Pearson تبدیل میان مول، گرم و تعداد ذره را بر مبنای واکنش موازنه‌شده ارائه می‌کند.[1]

| اولویت | قابلیت | ارزش کاربر | خروجی ملموس |
|---|---|---|---|
| P0 | تحلیل درصد جرمی عناصر | درک فوری ترکیب هر ماده و اعتبارسنجی جمع درصدها | جدول، نمودار میله‌ای افقی و خروجی CSV/PNG |
| P0 | تبدیل استوکیومتری | پاسخ‌گویی به پرسش‌های جرم-به-جرم، مول-به-مول و جرم-به-مول | مراحل محاسبه، واحدها و گرد کردن کنترل‌شده |
| P1 | واکنش‌دهندهٔ محدودکننده | پشتیبانی از سناریوهای آزمایشگاهی و صنعتی | شناساگر مادهٔ محدودکننده، مادهٔ اضافی و مقدار باقی‌مانده |
| P1 | بازده نظری و درصدی | پوشش آزمایش‌های آموزشی و کنترل فرآیند | کارت نتیجه، فرمول، هشدار واحد و گزارش PDF/CSV در آینده |
| P2 | نمودارهای واکنش | ارائهٔ بصری نسبت‌های مولی و ورودی/خروجی | Sankey یا نمودار ستونی، با حالت دادهٔ نمونه و حالت دادهٔ واقعی |

> **مرز علمی محصول:** نمودارها و محاسبات باید فقط از واکنش موازنه‌شده و مقادیر ورودی کاربر نتیجه‌گیری کنند. آن‌ها پیش‌بینی‌کنندهٔ محصول، سینتیک، تعادل یا ایمنی واکنش نیستند.

## طراحی قابلیت تحلیل درصدی عناصر

### روش محاسبه

برای هر ترکیب، سهم جرمی یک عنصر از رابطهٔ زیر به دست می‌آید:

> `درصد جرمی عنصر = (تعداد اتم × جرم اتمی عنصر ÷ جرم مولی ترکیب) × 100`

جمع تمام درصدها باید با تلورانس نمایش، برابر 100% باشد. راهنمای درصد ترکیب جرمی نیز همین رابطه را به‌صورت نسبت سهم جرمی عنصر به جرم مولی کل بیان می‌کند.[2]

| ستون جدول | تعریف | نمونه برای `CaCO3` |
|---|---|---|
| عنصر | نماد استاندارد عنصر | `Ca`، `C`، `O` |
| تعداد اتم | تعداد اتم عنصر در یک واحد فرمولی | `1`، `1`، `3` |
| جرم اتمی | مقدار جدول جرمی موجود در هستهٔ برنامه | `40.078` برای Ca |
| سهم جرمی | `تعداد × جرم اتمی` | `40.078 g/mol` برای Ca |
| درصد جرمی | `سهم ÷ جرم مولی × 100` | حدود `40.04%` برای Ca |

در رابط کاربری، این جدول در کنار یک **نمودار میله‌ای افقی رنگی و قابل‌دسترسی** نمایش داده می‌شود؛ برچسب‌های نمودار باید نام عنصر، درصد دقیق و رنگ مستقل از معنی باشند تا وابستگی به ادراک رنگ ایجاد نشود. در نسخهٔ اول، نمودار دایره‌ای را گزینهٔ اصلی توصیه نمی‌کنم، زیرا مقایسهٔ سهم‌های نزدیک در نمودار میله‌ای دقیق‌تر و در ابعاد کوچک خواناتر است.

### اجزای پیشنهادی در کد

| ماژول | مسئولیت | نکتهٔ کیفی |
|---|---|---|
| `analysis.py` | `elemental_composition(formula)` و مدل دادهٔ سهم جرمی | از `parse_species` و `ATOMIC_WEIGHTS` فعلی استفاده کند؛ هیچ منطق محاسباتی در ویجت UI قرار نگیرد. |
| `stoichiometry.py` | تبدیل واحد، نسبت مولی، محدودکننده و بازده | برای مقادیر کاربر از `Decimal` استفاده کند تا سیاست گرد کردن روشن و قابل‌آزمون باشد. |
| `charts.py` | تولید دادهٔ قابل‌رسم و تصویر/بردار خروجی | داده و ارائهٔ بصری را تفکیک کند تا منطق بدون Qt قابل‌آزمون بماند. |
| `app.py` | تب جدید «Analysis» و تعامل کاربر | همیشه واحد، تعداد رقم اعشار و منبع مقدار را در UI نمایان کند. |
| `test_analysis.py` | پوشش واحدهای تبدیل و خطاها | شامل تست جمع 100%، فرمول‌های هیدراته و عناصر تکراری باشد. |

نمونهٔ API مستقل و آزمون‌پذیر:

```python
from dataclasses import dataclass
from decimal import Decimal

from chembalance import ATOMIC_WEIGHTS, parse_species

@dataclass(frozen=True)
class CompositionRow:
    element: str
    atom_count: int
    mass_contribution: Decimal
    mass_percent: Decimal


def elemental_composition(formula: str) -> list[CompositionRow]:
    species = parse_species(formula)
    total = sum(
        Decimal(str(ATOMIC_WEIGHTS[element])) * count
        for element, count in species.atoms.items()
    )
    return [
        CompositionRow(
            element=element,
            atom_count=count,
            mass_contribution=Decimal(str(ATOMIC_WEIGHTS[element])) * count,
            mass_percent=(Decimal(str(ATOMIC_WEIGHTS[element])) * count / total * Decimal("100")),
        )
        for element, count in sorted(species.atoms.items())
    ]
```

### طراحی نمودارهای استوکیومتری

نمودار باید از یک مسئلهٔ مشخص آغاز شود، نه از دادهٔ ساختگی. در تب **Stoichiometry**، کاربر واکنش موازنه‌شده را انتخاب می‌کند، یک گونهٔ مبنا، مقدار ورودی و واحد را وارد می‌کند، سپس گونهٔ هدف و واحد خروجی را تعیین می‌کند. محصول، کارت‌های تبدیل گام‌به‌گام، جدول نسبت‌ها و یک نمودار ستونی ورودی/خروجی خواهد بود.

| نمودار | زمان نمایش | دادهٔ لازم | تصمیم طراحی |
|---|---|---|---|
| سهم جرمی عناصر | هر زمان یک ترکیب انتخاب شده است | فرمول و جرم‌های اتمی | میلهٔ افقی با درصد و جدول همراه |
| نسبت مولی واکنش | پس از موازنه | ضرایب واکنش | میلهٔ ستونی «به ازای یک واحد واکنش» |
| تبدیل مقدار | پس از ورود مقدار و واحد | گونهٔ مبنا، گونهٔ هدف، مقدار | نمودار ستونی مقایسه‌ای؛ واحدها باید روی محور/برچسب ذکر شوند |
| واکنش‌دهندهٔ محدودکننده | فقط با حداقل دو ورودی واکنش‌دهنده | مقادیر اولیه | میلهٔ مصرف‌شده و باقی‌مانده، همراه با نتیجهٔ نوشتاری |

## برنامهٔ تحویل نسخهٔ v1.1

| اسپرینت | دامنه | معیار پذیرش |
|---|---|---|
| 1 | مدل‌های داده، درصد جرمی عناصر، تست‌های واحد | جمع درصد هر فرمول با دقت نمایش به 100% برسد؛ هیدرات و گروه‌های تو‌در‌تو پوشش داده شوند. |
| 2 | تب Analysis، جدول و نمودار ترکیب | کاربر بتواند ترکیب یک ماده را کپی و به CSV صادر کند؛ همهٔ نمودارها برچسب قابل‌خواندن داشته باشند. |
| 3 | تبدیل‌های مول/جرم و نسبت‌های واکنش | مسیر تبدیل و واحد در هر مرحله نمایش داده شود؛ ورودی نامعتبر با پیام عملیاتی رد شود. |
| 4 | محدودکننده، بازده و QA | سناریوهای کلاسیک آموزشی، آزمون UI، آزمون رگرسیون و بازبینی دسترس‌پذیری تکمیل شوند. |

## راهبرد CI/CD برای Windows، macOS و Linux

### اصل معماری

هر فایل اجرایی باید **روی سیستم‌عامل هدف خودش ساخته شود**. GitHub Actions با `strategy.matrix` می‌تواند برای هر ترکیب سیستم‌عامل و نسخهٔ زبان یک Job مستقل بسازد.[3] برای ChemBalance، آزمون منطقی می‌تواند روی چند نسخهٔ Python در Ubuntu اجرا شود؛ اما بسته‌های قابل‌توزیع باید به‌صورت native روی `windows-latest`، `macos-13`، `macos-14` و `ubuntu-22.04` ساخته شوند.

| پلتفرم | Runner پیشنهادی | دارایی انتشار | دلیل |
|---|---|---|---|
| Windows x64 | `windows-latest` | `ChemBalance-windows-x64.zip` | ساخت `ChemBalance.exe` به‌صورت native و بستهٔ ZIP ساده برای کاربر. |
| macOS Intel | `macos-13` | `ChemBalance-macos-x64.zip` | پوشش دستگاه‌های Intel؛ بسته شامل `.app` است. |
| macOS Apple Silicon | `macos-14` | `ChemBalance-macos-arm64.zip` | پوشش native برای Macهای Apple Silicon. |
| Linux x64 | `ubuntu-22.04` | `ChemBalance-linux-x64.tar.gz` | سازگاری ABI محافظه‌کارانه‌تر نسبت به runnerهای خیلی جدید. |

### گردش‌کار پیشنهادی

فایل فعلی `windows-release.yml` را به `desktop-release.yml` تغییر دهید و محتوای زیر را جایگزین کنید. این نسخه در هر Push و Pull Request آزمون‌های منطقی را اجرا می‌کند، اما فقط هنگام Push یک تگ `v*` دارایی‌های چندسکویی را در GitHub Release منتشر می‌سازد.

```yaml
name: Build and release ChemBalance Desktop

on:
  push:
    branches: [main]
    tags: ["v*"]
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  test:
    name: Test core (${{ matrix.python-version }})
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: python -m unittest -v

  build-windows:
    name: Package Windows x64
    if: startsWith(github.ref, 'refs/tags/v')
    needs: test
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install --upgrade pip -r requirements.txt
      - env:
          QT_QPA_PLATFORM: offscreen
        run: python ui_smoke_test.py
      - run: python -m PyInstaller --noconfirm --clean --windowed --name ChemBalance app.py
      - shell: pwsh
        run: |
          Compress-Archive -Path dist/ChemBalance/* -DestinationPath dist/ChemBalance-windows-x64.zip -Force
          (Get-FileHash dist/ChemBalance-windows-x64.zip -Algorithm SHA256).Hash.ToLower() + "  ChemBalance-windows-x64.zip" |
            Out-File -Encoding ascii dist/ChemBalance-windows-x64.zip.sha256
      - uses: actions/upload-artifact@v4
        with:
          name: release-windows-x64
          path: dist/ChemBalance-windows-x64.zip*
          if-no-files-found: error

  build-macos:
    name: Package macOS (${{ matrix.name }})
    if: startsWith(github.ref, 'refs/tags/v')
    needs: test
    strategy:
      fail-fast: false
      matrix:
        include:
          - name: x64
            runner: macos-13
          - name: arm64
            runner: macos-14
    runs-on: ${{ matrix.runner }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install --upgrade pip -r requirements.txt
      - env:
          QT_QPA_PLATFORM: offscreen
        run: python ui_smoke_test.py
      - run: python -m PyInstaller --noconfirm --clean --windowed --name ChemBalance app.py
      - run: |
          ditto -c -k --sequesterRsrc --keepParent \
            dist/ChemBalance.app dist/ChemBalance-macos-${{ matrix.name }}.zip
          shasum -a 256 dist/ChemBalance-macos-${{ matrix.name }}.zip \
            > dist/ChemBalance-macos-${{ matrix.name }}.zip.sha256
      - uses: actions/upload-artifact@v4
        with:
          name: release-macos-${{ matrix.name }}
          path: dist/ChemBalance-macos-${{ matrix.name }}.zip*
          if-no-files-found: error

  build-linux:
    name: Package Linux x64
    if: startsWith(github.ref, 'refs/tags/v')
    needs: test
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install --upgrade pip -r requirements.txt
      - env:
          QT_QPA_PLATFORM: offscreen
        run: python ui_smoke_test.py
      - run: python -m PyInstaller --noconfirm --clean --windowed --name ChemBalance app.py
      - run: |
          tar -C dist -czf dist/ChemBalance-linux-x64.tar.gz ChemBalance
          sha256sum dist/ChemBalance-linux-x64.tar.gz > dist/ChemBalance-linux-x64.tar.gz.sha256
      - uses: actions/upload-artifact@v4
        with:
          name: release-linux-x64
          path: dist/ChemBalance-linux-x64.tar.gz*
          if-no-files-found: error

  release:
    name: Publish GitHub Release
    if: startsWith(github.ref, 'refs/tags/v')
    needs: [build-windows, build-macos, build-linux]
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/download-artifact@v4
        with:
          pattern: release-*
          path: release-assets
          merge-multiple: true
      - uses: softprops/action-gh-release@v2
        with:
          generate_release_notes: true
          body: |
            ## ChemBalance Desktop

            Download the archive for your operating system and verify it against the accompanying SHA-256 file when required.

            - **Windows:** extract the ZIP and run `ChemBalance.exe`.
            - **macOS:** download the ZIP matching your processor (Intel or Apple Silicon), extract it, then open `ChemBalance.app`.
            - **Linux:** extract the TAR.GZ and run `ChemBalance/ChemBalance`.
          files: release-assets/*
```

### مراحل عملی استقرار

| گام | اقدام | توضیح |
|---|---|---|
| 1 | نام فایل workflow را تغییر دهید | فایل جدید را در `.github/workflows/desktop-release.yml` قرار دهید و workflow صرفاً ویندوزی قدیمی را حذف کنید تا دو انتشار هم‌زمان رخ ندهد. |
| 2 | روی Pull Request آزمایش کنید | چون Jobهای بسته‌بندی فقط برای tag اجرا می‌شوند، PR فقط آزمون سریع هسته را اجرا خواهد کرد. برای آزمایش build پیش از release می‌توانید شرط `if` را موقتاً بردارید یا `workflow_dispatch` جدا بسازید. |
| 3 | ابتدا release آزمایشی بسازید | تگ `v1.1.0-rc.1` را Push کنید و خروجی‌های macOS و Linux را روی دستگاه‌های واقعی بررسی کنید. |
| 4 | release نهایی را منتشر کنید | بعد از تأیید دارایی‌ها، `v1.1.0` را Push کنید تا تمام فایل‌ها و checksumها به یک Release متصل شوند. |
| 5 | سیاست نگهداری را تثبیت کنید | Python و GitHub Actions را به‌صورت ماهانه به‌روزرسانی کنید و ABI لینوکس و سازگاری macOS را در هر release آزمایش کنید. |

### امضای کد و اعتماد کاربر

در Windows، گام بعدی تجاری تهیهٔ گواهی code-signing و امضای `ChemBalance.exe` در runner ویندوز است. در macOS، برای توزیع خارج از App Store، Apple استفاده از گواهی Developer ID را برای القای اعتماد به کاربر توصیه می‌کند؛ Apple همچنین توضیح می‌دهد که notarization برای اجرای مناسب تحت Gatekeeper و توزیع حرفه‌ای اهمیت دارد.[4]

امضای macOS را **پس از آن‌که build پایه‌ای روی هر دو معماری پایدار شد** اضافه کنید. گواهی و رمزها نباید در YAML ذخیره شوند؛ آن‌ها را به GitHub Secrets منتقل کنید. برای Linux می‌توان checksum را از همان ابتدا منتشر کرد و در مرحلهٔ بعدی امضای GPG یا Sigstore را به چرخه اضافه کرد.

| دارایی محرمانه | محل نگهداری | نکتهٔ اجرایی |
|---|---|---|
| گواهی Windows Code Signing | GitHub Actions Secrets یا سرویس امضای ابری | هیچ‌گاه فایل PFX یا گذرواژه را در مخزن قرار ندهید. |
| گواهی Developer ID macOS | GitHub Actions Secrets | فقط در Job macOS برای ایجاد keychain موقت مصرف شود. |
| حساب notarization اپل | GitHub Actions Secrets | بهتر است از App Store Connect API key با محدودیت دامنه استفاده شود. |
| کلید GPG/Sigstore | GitHub Actions Secrets یا OIDC | کلید عمومی و دستور اعتبارسنجی را همراه release منتشر کنید. |

## معیارهای موفقیت v1.1

نسخهٔ بعدی زمانی آمادهٔ انتشار است که کاربر بتواند برای یک فرمول پیچیده، درصدهای جرمی را مشاهده کند و مجموع آن‌ها برابر 100% باشد؛ برای یک واکنش موازنه‌شده تبدیل جرمی یا مولی را با مسیر محاسبهٔ قابل‌پیگیری انجام دهد؛ و از همان tag، دارایی‌های Windows x64، macOS Intel، macOS Apple Silicon و Linux x64 به همراه checksum تولید شوند.

## منابع

[1]: https://www.pearson.com/channels/calculators/stoichiometry-calculator "Pearson — Stoichiometry Calculator"
[2]: https://chem.libretexts.org/Courses/University_of_Arkansas_Little_Rock/Chem_1402%3A_General_Chemistry_1_(Kattoum)/Text/2%3A_Atoms%2C_Molecules%2C_and_Ions/5.13%3A_Percent_Composition "LibreTexts — Percent Composition"
[3]: https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations "GitHub Docs — Running variations of jobs in a workflow"
[4]: https://help.apple.com/xcode/mac/current/en.lproj/dev033e997ca.html "Apple — Distribute outside the Mac App Store"

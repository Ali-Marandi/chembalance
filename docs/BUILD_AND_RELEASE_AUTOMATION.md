# راهنمای ساخت و انتشار خودکار ChemBalance

## آنچه پیاده‌سازی شده است

زیرساخت جدید در دو بخش عمل می‌کند. اسکریپت [`scripts/package_desktop.py`](../scripts/package_desktop.py) روی **سیستم‌عامل هدف**، برنامهٔ دسکتاپ را با PyInstaller می‌سازد، آن را در آرشیو مناسب قرار می‌دهد و یک فایل SHA-256 همراه آن می‌نویسد. گردش‌کار [`desktop-release.yml`](../.github/workflows/desktop-release.yml) این اسکریپت را در GitHub Actions روی runnerهای native اجرا، دارایی‌ها را تجمیع و برای tagهای نسخه در GitHub Releases منتشر می‌کند.

| پلتفرم | runner | آرشیو نهایی | دستور نصب کاربر |
|---|---|---|---|
| Windows x64 | `windows-latest` | `ChemBalance-windows-x64.zip` | استخراج ZIP و اجرای `ChemBalance.exe` |
| macOS Intel | `macos-13` | `ChemBalance-macos-x64.zip` | استخراج ZIP و باز کردن `ChemBalance.app` |
| macOS Apple Silicon | `macos-14` | `ChemBalance-macos-arm64.zip` | استخراج ZIP و باز کردن `ChemBalance.app` |
| Linux x64 | `ubuntu-22.04` | `ChemBalance-linux-x64.tar.gz` | استخراج TAR.GZ و اجرای `ChemBalance/ChemBalance` |

> PyInstaller یک cross-compiler نیست. هر دارایی در workflow روی همان سیستم‌عامل و معماری هدف ساخته می‌شود؛ به همین دلیل، خروجی macOS روی runnerهای macOS و خروجی Windows روی runner ویندوز ساخته می‌شود.

## جریان‌های خودکار

| رویداد GitHub | خروجی workflow |
|---|---|
| Pull Request به `main` | نصب وابستگی‌ها و اجرای مجموعهٔ آزمون کامل روی Python 3.10 تا 3.13 |
| Push به `main` | همان کنترل کیفیت چندنسخه‌ای، بدون انتشار فایل |
| اجرای دستی (`workflow_dispatch`) | ساخت آرشیوهای native و بارگذاری آن‌ها به‌عنوان Actions Artifact، بدون انتشار عمومی Release |
| Push تگ `v*` | آزمون، ساخت چهار دارایی native، تولید checksum و انتشار خودکار در GitHub Releases |

## انتشار نسخهٔ جدید

قبل از انتشار، مطمئن شوید CI شاخهٔ `main` سبز است و CHANGELOG به‌روز شده است. سپس از ماشین توسعهٔ خود اجرا کنید:

```bash
git checkout main
git pull --ff-only
git tag -a v1.1.0 -m "ChemBalance Desktop v1.1.0"
git push origin v1.1.0
```

GitHub Actions به‌صورت خودکار چهار آرشیو و چهار فایل checksum تولید می‌کند. صفحهٔ Release را پس از تکمیل workflow باز کنید و فقط این چهار موضوع را کنترل نمایید: نام و معماری فایل‌ها، وجود checksum کنار هر فایل، توضیح نصب و یادداشت محدودهٔ علمی محصول.

## ساخت محلی

برای تست native روی Linux x64:

```bash
python -m pip install --upgrade pip -r requirements.txt
MPLBACKEND=Agg python scripts/package_desktop.py --platform linux-x64
cd dist/release
sha256sum --check ChemBalance-linux-x64.tar.gz.sha256
```

برای Windows و macOS همان دستور را با `--platform windows-x64`، `--platform macos-x64` یا `--platform macos-arm64` روی سیستم‌عامل و معماری هدف اجرا کنید. اسکریپت در صورت اجرا روی host اشتباه، قبل از ساخت با پیام صریح متوقف می‌شود.

## امنیت و امضای کد

checksum به کاربر امکان کنترل یکپارچگی فایل دانلودی را می‌دهد، اما جایگزین امضای کد نیست. قبل از توزیع تجاری گسترده، این مراحل توصیه می‌شود:

| پلتفرم | اقدام بعدی | محل نگهداری محرمانه |
|---|---|---|
| Windows | امضای `ChemBalance.exe` با گواهی code-signing در job ویندوز | GitHub Actions Secrets یا سرویس امضای ابری |
| macOS | امضای Developer ID، notarization و stapling برای هر `.app` | GitHub Actions Secrets؛ هرگز داخل مخزن یا YAML |
| Linux | انتشار SHA-256 در همهٔ نسخه‌ها؛ سپس افزودن امضای GPG یا Sigstore | کلید خصوصی یا OIDC، خارج از مخزن |

Apple برای توزیع خارج از App Store، استفاده از Developer ID و notarization را به‌عنوان مسیر اعتماد کاربر توضیح می‌دهد.[1] GitHub Actions نیز از راهبرد matrix برای اجرای variationهای native روی چند سیستم‌عامل پشتیبانی می‌کند.[2]

## کنترل کیفیت

گردش‌کار پیش از ساخت بستهٔ هر پلتفرم، آزمون رابط `ui_smoke_test.py` و مجموعهٔ کامل `unittest` را اجرا می‌کند. وابستگی `matplotlib` به‌طور صریح در `requirements.txt` ثبت شده است تا آزمون‌های تحلیل استوکیومتری نیز در CI تکرارپذیر باشند.

## منابع

[1]: https://help.apple.com/xcode/mac/current/en.lproj/dev033e997ca.html "Apple — Distribute outside the Mac App Store"
[2]: https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations "GitHub Docs — Running variations of jobs in a workflow"

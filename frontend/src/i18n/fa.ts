/** Persian (fa-IR) message catalog for the authentication pages. */
export const catalog = {
  'app.name': 'بازار لوازم جانبی موبایل',
  'login.title': 'ورود به حساب',
  'login.subtitle': 'بازار لوازم جانبی موبایل',
  'login.email': 'ایمیل',
  'login.password': 'رمز عبور',
  'login.submit': 'ورود',
  'login.submitting': 'در حال ورود…',
  'login.success': 'شما وارد حساب خود شدید.',
  'login.switchPrompt': 'حساب ندارید؟',
  'login.switchLink': 'ایجاد حساب',
  'register.title': 'ایجاد حساب',
  'register.subtitle': 'بازار لوازم جانبی موبایل',
  'register.email': 'ایمیل',
  'register.password': 'رمز عبور',
  'register.passwordHint': 'بین ۸ تا ۷۲ کاراکتر استفاده کنید.',
  'register.role': 'من یک',
  'register.roleBuyer': 'خریدار — مرور و خرید لوازم جانبی',
  'register.roleSeller': 'فروشنده — نمایش محصولاتم',
  'register.submit': 'ایجاد حساب',
  'register.submitting': 'در حال ایجاد حساب…',
  'register.success': 'حساب شما آماده است و وارد شده اید.',
  'register.switchPrompt': 'از قبل حساب دارید؟',
  'register.switchLink': 'ورود',
  'errors.invalid_credentials': 'ایمیل یا رمز عبور اشتباه است.',
  'errors.duplicate_email': 'حسابی با این ایمیل وجود دارد.',
  'errors.unauthorized': 'برای ادامه لطفاً وارد شوید.',
  'errors.invalid_token': 'جلسه شما نامعتبر است. لطفاً دوباره وارد شوید.',
  'errors.fallback': 'خطایی رخ داد. لطفاً دوباره تلاش کنید.',
} as const

export type MessageKey = keyof typeof catalog

export function t(key: MessageKey): string {
  return catalog[key]
}

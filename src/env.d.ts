interface Env {
  /** R2 绑定；在 wrangler.toml 中配置 [[r2_buckets]] 后生效 */
  IMAGES?: R2Bucket;
  /** R2 公网访问前缀，例如 https://pub-xxxx.r2.dev（无末尾斜杠） */
  PUBLIC_BASE_URL?: string;
}

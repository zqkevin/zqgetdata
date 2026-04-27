# 安全更新日志

## 2026-04-27

### 🔒 安全漏洞修复

#### CVE-2026-26007 - cryptography 库安全漏洞

**漏洞描述：**
- **影响版本**: cryptography < 46.0.5
- **修复版本**: cryptography >= 46.0.5
- **严重程度**: 高

**漏洞详情：**
cryptography 库在 46.0.5 之前的版本中，以下函数未验证公钥点是否属于预期的素数阶子群：
- `public_key_from_numbers()` / `EllipticCurvePublicNumbers.public_key()`
- `load_der_public_key()`
- `load_pem_public_key()`

这允许攻击者提供来自小阶子群的公钥点，可能导致：
1. **ECDH 共享密钥协商**：泄露私钥的最低有效位
2. **ECDSA 签名验证**：容易在小子群上伪造签名
3. **仅影响 SECT 曲线**（ cofactor > 1 的曲线）

**修复措施：**
已将 cryptography 从 46.0.3 升级到 47.0.0

```bash
pip install cryptography>=46.0.5
```

**影响范围：**
- 所有使用椭圆曲线加密（ECC）的功能
- JWT Token 生成和验证
- HTTPS/TLS 连接

**验证方法：**
```bash
pip show cryptography
# 应显示 Version: 47.0.0 或更高
```

---

### 📦 依赖包更新清单

| 包名 | 旧版本 | 新版本 | 更新原因 |
|------|--------|--------|----------|
| cryptography | 46.0.3 | 47.0.0 | 修复 CVE-2026-26007 安全漏洞 |
| pymysql | 1.1.0 | 1.1.1 | 保持最新版本 |

### ✅ 验证状态

- [x] cryptography 已升级到 47.0.0
- [x] API 服务正常运行
- [x] 所有功能测试通过
- [x] requirements.txt 已更新

### 🔍 后续建议

1. **定期更新依赖**：建议每月检查一次依赖包的安全更新
2. **使用依赖扫描工具**：可以考虑使用 `safety` 或 `pip-audit` 进行自动化安全检查
3. **监控 CVE 数据库**：关注项目依赖的关键安全漏洞

### 📚 相关资源

- [CVE-2026-26007 详细信息](https://nvd.nist.gov/vuln/detail/CVE-2026-26007)
- [cryptography 发布说明](https://cryptography.io/en/latest/changelog/)
- [Python 安全最佳实践](https://security.openstack.org/guidelines/dg_use-of-cryptography.html)

---

**更新日期**: 2026-04-27  
**更新人员**: AI Assistant  
**审核状态**: 已完成

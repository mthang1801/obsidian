<!-- tags: best-practice, production, testing, quality -->
# 🏗️ The Testing Pyramid — Chiến lược kiểm thử phần mềm

> "Writing code is easy now, but testing code is hard." — Tổng quan về các lớp kiểm thử từ Unit Test đến E2E Test và vai trò của AI trong quy trình testing hiện đại.

📅 Ngày tạo: 2026-03-22 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 10 phút đọc

| Aspect           | Detail                                              |
| ---------------- | --------------------------------------------------- |
| **Complexity**   | 🌟🌟                                                |
| **Use case**     | Xây dựng chiến lược test coverage cho dự án thực tế |
| **Go ecosystem** | `testing`, `testcontainers-go`, `testify`           |

---

## 1. DEFINE

CI pipeline: 847 tests, 45 phút chạy. 73% là E2E tests dùng Cypress. Mỗi lần fail, dev mất 30 phút debug — flaky vì network, timing, Docker startup. Kết quả: team bắt đầu ignore test failures, merge anyway. 2 tháng sau: production bug mà không test nào catch, vì unit test coverage chỉ 12%. Không phải thiếu test — thiếu đúng loại test ở đúng tầng.

Khi dự án bắt đầu lớn lên, câu hỏi không còn là “có test hay không” mà là “đổ nỗ lực test vào đâu để vẫn ship nhanh mà không tự phá mình”. `The Testing Pyramid` đáng đọc không phải vì nó là hình tam giác nổi tiếng, mà vì nó buộc đội kỹ thuật phải nói rõ mình đang mua confidence bằng loại test nào.

Nhiều codebase hỏng không phải vì thiếu test hoàn toàn. Chúng hỏng vì test portfolio lệch: quá nhiều E2E chậm và flaky, quá ít integration để bắt contract, hoặc unit tests quá mỏng để cho phép refactor an toàn. Best practice ở đây là chiến lược phân bổ, không phải thêm test một cách vô thức.

Core insight: **Testing pyramid chỉ có giá trị khi mỗi tầng test được giao đúng loại rủi ro nó nên bắt, thay vì bắt một tầng gánh thay mọi tầng còn lại.**

**Testing Pyramid (Kim tự tháp kiểm thử)** là một framework tư duy giúp định hình chiến lược phân bổ các loại test trong một dự án phần mềm nhằm tối ưu tốc độ, chi phí và độ ổn định.

- **Unit + Component Tests**: Nằm ở đáy tháp. Kiểm thử từng hàm (function) hoặc UI component một cách cô lập. Chúng rất nhanh, ít tốn kém để chạy và dễ bảo trì. Hầu hết test coverage của bạn nên đến từ tầng này. (Tools: Jest, Vitest, Go testing, Testify, JUnit).
- **Integration Tests**: Nằm ở giữa tháp. Kiểm chứng việc giao tiếp giữa các services, APIs và databases. Unit test sẽ không bắt được lỗi sai API validation, nhưng integration test sẽ bắt được. (Tools: Testcontainers, Postman, Supertest).
- **End-to-End (E2E) Tests**: Nằm trên đỉnh tháp. Xác thực toàn bộ hành trình người dùng (user journey) đi qua toàn bộ hệ thống thực. Chúng mất nhiều thời gian để chạy, dễ flaky (lúc pass lúc fail do mạng/DB) và đắt đỏ để maintain. Vì vậy, số lượng E2E test nên ít nhất. (Tools: Cypress, Playwright, Appium).

**Sự trưởng thành của AI Testing Tools:**
Các công cụ AI (GitHub Copilot, Cursor, Qodo, ChatGPT) đang dần trở thành một phần của quy trình kiểm thử. Chúng hỗ trợ phác thảo bản draft cho bài test, tự động lấp đầy coverage bị thiếu, quản lý những test-case lặp đi lặp lại — giải phóng developer để họ có thời gian tập trung vào các **edge cases** đặc thù có thể xảy ra trên production.

## 2. VISUAL

Pyramid dễ bị biến thành khẩu hiệu nếu không nhìn được cost và confidence đang đổi theo từng tầng như thế nào. Sơ đồ dưới đây làm rõ trade-off đó.

![Testing Pyramid — Risk Allocation](./images/12-testing-pyramid.png)

### Sơ đồ: The Testing Pyramid

```mermaid
pie title Phân bổ loại Test lý tưởng (The Testing Pyramid)
    "Unit + Component Tests" : 70
    "Integration Tests" : 20
    "End-to-End (E2E) Tests" : 10
```

```text
       ▲
      ∕ ∖       ← End-to-End (E2E) Tests: Playwright, Cypress, Appium
     ∕   ∖        (Đắt đỏ, chậm, số lượng ít nhất)
    ∕     ∖
   ∕───────∖    ← Integration Tests: Testcontainers, Postman, Supertest
  ∕         ∖     (Verify API contract, Database, External APIs)
 ∕───────────∖
∕             ∖ ← Unit + Component Tests: Jest, Vitest, Go testing, Testify
───────────────   (Nhanh, rẻ, isolated, số lượng nhiều nhất)
```

_(Ý tưởng cốt lõi: Số lượng bài test nên giảm dần theo chiều cao của tháp, trong khi chi phí thực thi và bảo trì sẽ tăng dần)_

## 3. CODE

Dưới đây là minh họa cho cả 3 tầng của kim tự tháp.

### 1. Tầng Đáy: Unit Test (Nhanh & Rẻ)

**Introduce trước:** Test logic tính discount thuần túy. KHÔNG kết nối external DB/APIs để đảm bảo tốc độ `O(1)`.

```go
package pricing

import (
	"testing"
	"github.com/stretchr/testify/assert"
)

// CalculateDiscount tính tiền giảm giá cho giỏ hàng
func CalculateDiscount(total float64, isVip bool) float64 {
	if total >= 1000 && isVip {
		return total * 0.2 // Giảm 20% cho VIP mua nhiều
	}
	if total >= 500 {
		return total * 0.1 // Giảm 10%
	}
	return 0
}

func TestCalculateDiscount(t *testing.T) {
	// AI có thể tự sinh ra Table-driven test này cực kỳ chuẩn xác
	tests := []struct {
		name     string
		total    float64
		isVip    bool
		expected float64
	}{
		{"VIP > 1000", 1200, true, 240},
		{"Normal > 1000", 1200, false, 120},
		{"Normal > 500", 600, false, 60},
		{"Low amount", 100, true, 0},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			discount := CalculateDiscount(tt.total, tt.isVip)
			assert.Equal(t, tt.expected, discount, "Discount không khớp")
		})
	}
}
```
```typescript
// pricing.ts
export function calculateDiscount(total: number, isVip: boolean): number {
    if (total >= 1000 && isVip) return total * 0.2; // 20% for VIP high-value
    if (total >= 500) return total * 0.1;           // 10%
    return 0;
}

// pricing.test.ts (Jest)
import { calculateDiscount } from './pricing';

describe('calculateDiscount', () => {
    // AI có thể tự sinh ra table-driven test này cực kỳ chuẩn xác
    const cases = [
        { name: 'VIP > 1000', total: 1200, isVip: true,  expected: 240 },
        { name: 'Normal > 1000', total: 1200, isVip: false, expected: 120 },
        { name: 'Normal > 500',  total: 600,  isVip: false, expected: 60  },
        { name: 'Low amount',    total: 100,  isVip: true,  expected: 0   },
    ];

    test.each(cases)('$name', ({ total, isVip, expected }) => {
        expect(calculateDiscount(total, isVip)).toBe(expected);
    });
});
```
```rust
// pricing.rs
pub fn calculate_discount(total: f64, is_vip: bool) -> f64 {
    if total >= 1000.0 && is_vip {
        return total * 0.2; // 20% for VIP high-value
    }
    if total >= 500.0 {
        return total * 0.1; // 10%
    }
    0.0
}

#[cfg(test)]
mod tests {
    use super::*;

    // Table-driven tests in Rust
    #[test]
    fn test_calculate_discount() {
        let cases = vec![
            ("VIP > 1000",    1200.0, true,  240.0),
            ("Normal > 1000", 1200.0, false, 120.0),
            ("Normal > 500",  600.0,  false,  60.0),
            ("Low amount",    100.0,  true,    0.0),
        ];

        for (name, total, is_vip, expected) in cases {
            let result = calculate_discount(total, is_vip);
            assert!(
                (result - expected).abs() < f64::EPSILON,
                "{}: expected {}, got {}",
                name, expected, result
            );
        }
    }
}
```
```cpp
// pricing.h
#pragma once

inline double calculate_discount(double total, bool is_vip) {
    if (total >= 1000.0 && is_vip) return total * 0.2;
    if (total >= 500.0) return total * 0.1;
    return 0.0;
}

// pricing_test.cpp (GoogleTest)
#include <gtest/gtest.h>
#include "pricing.h"

struct DiscountCase {
    const char* name;
    double total;
    bool is_vip;
    double expected;
};

class CalculateDiscountTest : public ::testing::TestWithParam<DiscountCase> {};

TEST_P(CalculateDiscountTest, ReturnsCorrectDiscount) {
    auto& tc = GetParam();
    EXPECT_DOUBLE_EQ(calculate_discount(tc.total, tc.is_vip), tc.expected)
        << tc.name;
}

INSTANTIATE_TEST_SUITE_P(
    DiscountCases,
    CalculateDiscountTest,
    ::testing::Values(
        DiscountCase{"VIP > 1000",    1200.0, true,  240.0},
        DiscountCase{"Normal > 1000", 1200.0, false, 120.0},
        DiscountCase{"Normal > 500",  600.0,  false,  60.0},
        DiscountCase{"Low amount",    100.0,  true,    0.0}
    )
);
```
```python
# pricing.py
def calculate_discount(total: float, is_vip: bool) -> float:
    if total >= 1000 and is_vip:
        return total * 0.2  # 20% for VIP high-value
    if total >= 500:
        return total * 0.1  # 10%
    return 0.0

# test_pricing.py (pytest)
import pytest

from pricing import calculate_discount

@pytest.mark.parametrize(
    ("name", "total", "is_vip", "expected"),
    [
        ("VIP > 1000", 1200, True, 240),
        ("Normal > 1000", 1200, False, 120),
        ("Normal > 500", 600, False, 60),
        ("Low amount", 100, True, 0),
    ],
)
def test_calculate_discount(name: str, total: float, is_vip: bool, expected: float) -> None:
    assert calculate_discount(total, is_vip) == expected, name
```

```java
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.stream.Stream;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

final class Pricing {
    private Pricing() {}

    static double calculateDiscount(double total, boolean isVip) {
        if (total >= 1000 && isVip) {
            return total * 0.2;
        }
        if (total >= 500) {
            return total * 0.1;
        }
        return 0.0;
    }
}

class PricingTest {
    static Stream<Arguments> discountCases() {
        return Stream.of(
            Arguments.of("VIP > 1000", 1200.0, true, 240.0),
            Arguments.of("Normal > 1000", 1200.0, false, 120.0),
            Arguments.of("Normal > 500", 600.0, false, 60.0),
            Arguments.of("Low amount", 100.0, true, 0.0)
        );
    }

    @ParameterizedTest(name = "{0}")
    @MethodSource("discountCases")
    void calculateDiscountReturnsExpectedValue(String name, double total, boolean isVip, double expected) {
        assertEquals(expected, Pricing.calculateDiscount(total, isVip), name);
    }
}
```

**Kết luận sau**: Chạy mất chưa tới `0.001s`. AI hoàn toàn có thể tự sinh code này, giúp dev tối ưu hóa productivity.

### 2. Tầng Giữa: Integration Test (Dùng Testcontainers)

**Introduce trước**: Đảm bảo Repository có thể gọi tới PostgreSQL thật để insert dữ liệu một cách an toàn mà không dính lỗi foreign-key hay syntax constraint.

```go
package repository

import (
	"context"
	"testing"
	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go/modules/postgres"
)

func TestUserRepo_Create_Integration(t *testing.T) {
	ctx := context.Background()

	// ✅ Tự động spin up một ephemeral PostgreSQL Docker container cho test
	pgContainer, err := postgres.RunContainer(ctx,
		postgres.WithDatabase("testdb"),
		postgres.WithUsername("user"),
		postgres.WithPassword("pass"),
	)
	require.NoError(t, err)
	defer pgContainer.Terminate(ctx)

	connStr, _ := pgContainer.ConnectionString(ctx)

	// Khởi tạo Repository với kết nối thật
	repo := NewUserRepository(connStr)
	repo.Migrate()

	// Tương tác thật với Database
	user := User{Name: "Alex", Email: "alex@email.com"}
	err = repo.Create(ctx, &user)

	// Khẳng định insert thành công và ID được trigger
	require.NoError(t, err)
	require.NotZero(t, user.ID)
}
```
```typescript
// user-repo.integration.test.ts (Jest + Supertest + Testcontainers)
import { PostgreSqlContainer } from '@testcontainers/postgresql';
import { Pool } from 'pg';
import { UserRepository } from './user.repository';

describe('UserRepository Integration', () => {
    let pool: Pool;
    let repo: UserRepository;
    let container: Awaited<ReturnType<PostgreSqlContainer['start']>>;

    beforeAll(async () => {
        // ✅ Tự động spin up PostgreSQL Docker container cho test
        container = await new PostgreSqlContainer()
            .withDatabase('testdb')
            .withUsername('user')
            .withPassword('pass')
            .start();

        pool = new Pool({ connectionString: container.getConnectionUri() });
        repo = new UserRepository(pool);
        await repo.migrate();
    }, 60_000); // Docker startup timeout

    afterAll(async () => {
        await pool.end();
        await container.stop();
    });

    it('should create user and return generated ID', async () => {
        const user = await repo.create({ name: 'Alex', email: 'alex@email.com' });

        // Khẳng định insert thành công và ID được trigger
        expect(user.id).toBeDefined();
        expect(user.id).toBeGreaterThan(0);
        expect(user.name).toBe('Alex');
    });
});
```
```rust
// user_repo_test.rs (sqlx + testcontainers-rs)
#[cfg(test)]
mod integration_tests {
    use sqlx::postgres::PgPoolOptions;
    use testcontainers::{clients::Cli, images::postgres::Postgres};

    use crate::repository::UserRepository;
    use crate::domain::CreateUserRequest;

    #[tokio::test]
    async fn test_create_user_integration() {
        // ✅ Tự động spin up PostgreSQL Docker container cho test
        let docker = Cli::default();
        let pg_image = Postgres::default()
            .with_db_name("testdb")
            .with_user("user")
            .with_password("pass");
        let container = docker.run(pg_image);

        let port = container.get_host_port_ipv4(5432);
        let conn_str = format!(
            "postgres://user:pass@localhost:{}/testdb",
            port
        );

        let pool = PgPoolOptions::new()
            .max_connections(5)
            .connect(&conn_str)
            .await
            .expect("Failed to connect to Postgres");

        let repo = UserRepository::new(pool.clone());
        repo.migrate().await.expect("Migration failed");

        // Tương tác thật với Database
        let user = repo
            .create(CreateUserRequest {
                name: "Alex".to_string(),
                email: "alex@email.com".to_string(),
            })
            .await
            .expect("Create user failed");

        // Khẳng định insert thành công và ID được trigger
        assert!(user.id > 0, "Expected generated ID > 0");
        assert_eq!(user.name, "Alex");
    }
}
```
```cpp
// user_repo_integration_test.cpp (GoogleTest + libpqxx)
// Requires: a real Postgres instance (use Docker or testcontainers-cpp)
#include <gtest/gtest.h>
#include <pqxx/pqxx>
#include "user_repository.h"

class UserRepositoryIntegrationTest : public ::testing::Test {
protected:
    void SetUp() override {
        // ✅ Connect to real Postgres (start via Docker before test)
        // docker run --rm -p 5432:5432 -e POSTGRES_PASSWORD=pass postgres:15
        conn_ = std::make_unique<pqxx::connection>(
            "host=localhost port=5432 dbname=testdb user=user password=pass"
        );
        repo_ = std::make_unique<UserRepository>(*conn_);
        repo_->migrate();
    }

    void TearDown() override {
        // Clean up test data
        pqxx::work txn(*conn_);
        txn.exec("DELETE FROM users WHERE email = 'alex@email.com'");
        txn.commit();
    }

    std::unique_ptr<pqxx::connection> conn_;
    std::unique_ptr<UserRepository> repo_;
};

TEST_F(UserRepositoryIntegrationTest, CreateUserReturnsGeneratedId) {
    // Tương tác thật với Database
    auto user = repo_->create("Alex", "alex@email.com");

    // Khẳng định insert thành công và ID được trigger
    EXPECT_GT(user.id, 0) << "Expected generated ID > 0";
    EXPECT_EQ(user.name, "Alex");
    EXPECT_EQ(user.email, "alex@email.com");
}
```
```python
# test_user_repository_integration.py (pytest + testcontainers + psycopg)
import psycopg
import pytest
from testcontainers.postgres import PostgresContainer

from user_repository import UserRepository

@pytest.fixture()
def repo() -> UserRepository:
    with PostgresContainer("postgres:15", username="user", password="pass", dbname="testdb") as pg:
        connection = psycopg.connect(pg.get_connection_url())
        repository = UserRepository(connection)
        repository.migrate()
        yield repository
        connection.close()

def test_create_user_integration(repo: UserRepository) -> None:
    user = repo.create({"name": "Alex", "email": "alex@email.com"})

    assert user["id"] > 0
    assert user["name"] == "Alex"
    assert user["email"] == "alex@email.com"
```

```java
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

class UserRepositoryIntegrationTest {
    static PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("testdb")
            .withUsername("user")
            .withPassword("pass");

    static UserRepository repo;

    @BeforeAll
    static void setUp() {
        postgres.start();
        repo = new UserRepository(postgres.getJdbcUrl(), postgres.getUsername(), postgres.getPassword());
        repo.migrate();
    }

    @AfterAll
    static void tearDown() {
        postgres.stop();
    }

    @Test
    void createUserReturnsGeneratedId() {
        User user = repo.create("Alex", "alex@email.com");

        assertTrue(user.id() > 0, "Expected generated ID > 0");
        assertEquals("Alex", user.name());
        assertEquals("alex@email.com", user.email());
    }
}
```

**Kết luận sau**: Chạy test mất vài giây do phải khởi tạo Docker. Tuy chậm hơn Unit Test, nó bắt được các lỗi Schema/SQL mà Mocking trong Unit Test sẽ lọt sổ (false positive).

### 3. Tầng Cao Nhất: E2E Test (Playwright)

**Introduce trước**: Giả lập trình duyệt (Frontend) thao tác UI từ lúc thêm vào giỏ hàng đến khi checkout, xuyên suốt cả Backend Server + DB.

```typescript
// tests/checkout.spec.ts (Ví dụ Test Runner Playwright)
import { test, expect } from '@playwright/test';

test('User can complete checkout payment successfully', async ({ page }) => {
    // 1. Visit Web App UI
    await page.goto('http://localhost:3000');

    // 2. Click button như user thật
    await page.click('text=Products');
    await page.click('button:has-text("Add To Cart")');
    await page.click('text=Checkout');

    // 3. Fill form giả
    await page.fill('input[name="cardNumber"]', '4242424242424242');
    await page.click('button:has-text("Pay Now")');

    // 4. Mất vài giây chờ Gateway trả response

    // 5. Verify kết quả end-state hiển thị đúng
    await expect(page.locator('.success-message')).toHaveText('Payment successful!');
});
```

**Kết luận sau**: Tầng này tốn rất nhiều thời gian chạy (chục giây đến phút). Nếu UI đổi tên CSS/Class, test sẽ chết (flaky). Cần giữ E2E ngắn gọn với những User Journeys quan trọng nhất (như Login, Checkout).

## 4. PITFALLS

Sai lầm trong strategy test thường không nằm ở cú pháp framework, mà ở chỗ một tầng test bị dùng sai vai trò và đội vẫn tưởng coverage là đủ.

| # | Severity | Lỗi (Pitfall) | Hậu quả | Fix (Giải pháp) |
| --- | --- | --- | --- | --- |
| 1 | 🟡 Common | **Ice Cream Cone Anti-pattern** | Dự án viết quá nhiều E2E Test và bỏ bê Unit Test. Hậu quả: CI/CD build tốn vài tiếng đồng hồ, release chậm, test cực kỳ flaky. | ✅ Lật ngược trở lại theo đúng Pyramid. Push các logics xuống tầng Unit Test càng nhiều càng tốt. |
| 2 | 🟡 Common | **Unit test mock mọi thứ (Mocking Hell)** | Khi DB đổi schema column, Unit test vẫn pass nhưng chạy lên Server là lỗi SQL. (False Positives). | ✅ Hạn chế mock Service hay Repositories quá nhiều. Tích cực dùng In-memory Test (SQLite) hoặc Testcontainers cho tầng DB Integration. |
| 3 | 🟡 Common | **AI sinh Test rác (Lazy Prompting)** | Dùng AI sinh test mù quáng dẫn đến sinh ra các bài test vô dụng như kiểm chứng struct properties mà không test logic behavior edge cases (như null pointers). | ✅ Dev phải code review những bài test từ AI. Chạy Code Coverage (đảm bảo Branch-coverage > 80%) để đo hiệu quả thật. |

## 5. REF

| Resource                                  | Link                                                                              |
| ----------------------------------------- | --------------------------------------------------------------------------------- |
| Martin Fowler: The Practical Test Pyramid | [MartinFowler.com](https://martinfowler.com/articles/practical-test-pyramid.html) |
| Testcontainers Core                       | [testcontainers.com](https://testcontainers.com/)                                 |
| Playwright E2E Testing                    | [playwright.dev](https://playwright.dev/)                                         |
| Go Testing Official Guide                 | [go.dev/doc/tutorial/add-a-test](https://go.dev/doc/tutorial/add-a-test)          |

## 6. RECOMMEND

Khi pyramid đã rõ, bước tiếp theo là nối nó sang testcontainers, contract testing, CI budgeting, và production observability để confidence không chỉ dừng ở pre-deploy.

| Mở rộng                     | Khi nào cần                                              | Lý do                                                                                                                                                                 |
| --------------------------- | -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Chaos Engineering**       | Khi hệ thống đạt scale rất lớn (Microservices)           | Đỉnh cao hơn E2E: Tắt ngẫu nhiên các dịch vụ (network partition, sập node) khi đang chạy production để xem hệ thống tồn tại được không. (VD: Gremlin, Chaos Monkey).  |
| **Contract Testing (Pact)** | Khi chia Frontend và Backend cho > 2 Teams/Repos độc lập | Đảm bảo nếu Team Backend đổi cấu trúc API Response, Team Frontend sẽ thấy Test fail ngay lập tức thông qua Contract Sharing mà không cần dựng instance DB/Server lên. |
| **Fuzzing (A.I Fuzz Test)** | Khi bảo vệ bộ Core Utility/Logic thư viện dùng chung     | Tự động sinh hàng triệu inputs rác/ngẫu nhiên (Go Fuzzing) để đẩy vào hàm, giúp đánh hơi các panics/OOM ngầm.                                                         |

---

## 7. QUICK REF

| # | Pattern | Tool / Rule |
|---|---------|-------------|
| 1 | **Phân bổ lý tưởng** | 70% Unit · 20% Integration · 10% E2E |
| 2 | **Unit test** | Fast, isolated, mock external dependencies — `testify/mock` |
| 3 | **Integration test** | Real DB + Redis: `testcontainers-go` — test actual SQL, actual cache |
| 4 | **E2E test** | Critical user journeys only — Playwright / Cypress |
| 5 | **Table-driven tests** | `for _, tc := range testCases { t.Run(tc.name, func(t *testing.T) {...}) }` |
| 6 | **Testcontainers** | `postgres.RunContainer(ctx)` — real Postgres trong Docker |
| 7 | **AI tools** | Draft tests, fill coverage gaps, xử lý repetitive cases — engineer focus vào edge cases |
| 8 | **Golden rule** | "Test behavior, not implementation" — test contract, không test internal code |

---

---

**Callback**: Quay lại 847 tests, 45 phút, 73% E2E lúc đầu. Bây giờ bạn biết: lật pyramid — 70% unit, 20% integration, 10% E2E. Test behavior không phải implementation. Và coverage 80% meaningful hơn 100% vanity metric.

← Quay về [Best Practices](./README.md) · ← Trước: [Memory Leak Silent](./11-memory-leak-silent.md)
## 8. INTERVIEW ANGLE

**System design / technical questions liên quan:**
- *"What is your testing strategy for a microservice?"*
- *"How do you test database interactions without hitting a real DB?"*
- *"What's the difference between unit, integration, and E2E tests?"*

**Điểm interviewer muốn nghe:**

| Chủ đề | Talking point |
|--------|---------------|
| **Testing Pyramid rationale** | 70/20/10 phân bổ: unit (fast/cheap) → integration (real deps) → E2E (user journey) |
| **Mock vs real DB** | Mocking DB schema changes không detect — testcontainers spin up real Postgres |
| **Ice cream cone anti-pattern** | Quá nhiều E2E → CI/CD build hàng tiếng, test flaky, release chậm |
| **When to use each** | Unit: business logic; Integration: repository/API layer; E2E: checkout flow, login |
| **AI tools role** | Draft boilerplate tests, fill coverage gaps — engineer focus vào edge cases |
| **Test behavior not implementation** | Test contract/output, không test internal code — survive refactoring |

**Follow-up questions thường gặp:**
- *"How do you handle flaky tests?"* → Identify root cause (timing, network), fix or delete if can't fix
- *"What coverage % do you aim for?"* → 80% branch coverage meaningful; 100% là vanity metric
- *"How do you test a third-party integration?"* → Contract test (Pact) + integration test với WireMock/real sandbox

---

## 10. DETECTION CHECKLIST

Khi test suite có vấn đề — dùng checklist này để diagnose:

| # | Triệu chứng | Nguyên nhân | Fix |
|---|-------------|-------------|-----|
| 1 | **E2E flaky > 20%** | Quá nhiều E2E test, phụ thuộc network/timing | Chuyển xuống integration test |
| 2 | **Unit pass, integration fail** | Thiếu integration coverage — mock quá nhiều | Thêm testcontainers tests |
| 3 | **CI chạy > 30 phút** | Quá nhiều slow tests (integration/E2E) | Parallelize + tăng unit, giảm E2E |
| 4 | **Coverage > 90% nhưng bug production** | Test sai layer — unit test mà nên là integration | Kiểm tra phân bổ 70/20/10 |
| 5 | **Tests break khi refactor** | Test implementation detail thay vì behavior | Test output/behavior, không test internals |

---


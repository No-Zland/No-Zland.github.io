#include <cstdio>

typedef long long ll;
const int MOD = 1000000007;
const int MAXF = 1300000;  // 2*6e5 足够：n - (m-2)k <= n + 2k <= 2n

static ll fact[MAXF], inv_fact[MAXF];

ll qpow(ll a, ll e) {
    ll r = 1 % MOD;
    a %= MOD;
    while (e > 0) {
        if (e & 1) r = r * a % MOD;
        a = a * a % MOD;
        e >>= 1;
    }
    return r;
}

void init() {
    fact[0] = 1;
    for (int i = 1; i < MAXF; i++) fact[i] = fact[i - 1] * i % MOD;
    inv_fact[MAXF - 1] = qpow(fact[MAXF - 1], MOD - 2);
    for (int i = MAXF - 1; i > 0; i--) inv_fact[i - 1] = inv_fact[i] * i % MOD;
}

inline ll C(ll N, ll K) {
    if (K < 0 || N < 0 || K > N) return 0;
    if (N >= MAXF) return 0;
    return fact[N] * inv_fact[K] % MOD * inv_fact[N - K] % MOD;
}

int main() {
    init();
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        ll n, m;
        scanf("%lld %lld", &n, &m);
        ll ans = (n >= m) ? ((n - m + 1) % MOD) : 0;  // k = 1
        for (ll k = 2; k * m <= n; k++) {
            ll two_k = 2 * k;
            ll a1 = n - (m - 2) * k;  // n - k*m + 2k
            ll a2 = n - (m - 1) * k;  // n - k*m + k
            ans += C(a1, two_k) - C(a2, two_k);
            ans %= MOD;
        }
        ans = ((ans % MOD) + MOD) % MOD;
        printf("%lld\n", ans);
    }
    return 0;
}

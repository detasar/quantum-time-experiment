# Araştırma Spesifikasyonu v1.0

## Objective Clock Bases from Redundant Records: Why Temporal Order Requires More

**Belge durumu:** Uygulamaya hazır, theorem-first araştırma protokolü  
**Tarih:** 20 Haziran 2026  
**Hedef çıktı:** Teori + exact klasik deneyler + lokal/noisy kuantum simülasyonu + koşullu tek IBM batch + sonuç-temelli makale kararı  
**Araştırma ilkesi:** Pozitif ve negatif sonuçlar aynı derecede önceden tanımlanmış bilimsel çıktılara bağlanacaktır.

---

# 0. Yönetici kararı

Bu çalışma aşağıdaki güçlü fakat sınırlı hipotezi test eder:

> Sonlu, global olarak tek bir statik history state ile temsil edilen bir sistem birden fazla matematiksel relational-clock decomposition destekleyebilir. Sabit ve fiziksel olarak gerekçelendirilmiş bir subsystem partition altında, birbirinden bağımsız erişilebilen, nondegenerate ve faithful redundant records en fazla bir **objective clock basis** seçebilir. Ancak bu basis tek başına clock label’larının temporal order’ını veya orientation’ını belirlemez. Order ve orientation, ancak persistent record içeriklerinin oluşturduğu yönlü yapının izin verdiği ölçüde tanımlanabilir.

Bu çalışma dört ayrı problemi kesin biçimde ayırır:

1. **Basis selection:** hangi PVM/basis lokal kayıtlar tarafından objektif olarak yayınlanmaktadır?
2. **Label identification:** seçilen basis’in outcome’ları hangi operasyonel record signatures’a karşılık gelir?
3. **Order identification:** bu label’lar persistent record accumulation ile hangi partial/total order’a yerleşir?
4. **Orientation identification:** order’ın hangi yönünün “daha önce → daha sonra” olduğu hangi fiziksel asymmetry ile sabitlenir?

## 0.1 Ana yenilik hedefi

Redundant record’ların bir observable/pointer basis seçmesi literatürde bilinen ve bu çalışma tarafından yeniden keşfedilmeyecek bir sonuçtur. Ana özgünlük hedefleri şunlardır:

- objective clock basis ile temporal order/orientation arasındaki ayrımı formalize etmek;
- persistent record signatures’dan elde edilebilecek **maksimal operasyonel temporal poset**’i karakterize etmek;
- persistent records ile uyumlu gerçek trajectories’in bu poset içindeki chains olduğunu göstermek;
- unique order için gerekli ve yeterli koşulu vermek;
- finite persistent-record capacity için kesin alt sınırlar vermek;
- partition serbestliğinin clock uniqueness’i neden yok ettiğini açık bir no-go ile göstermek;
- küçük bir GHZ history state üzerinde objective local basis ile nonlocal coherent alternative decomposition arasındaki farkı deneysel olarak göstermek.

## 0.2 Açıkça yapılmayacak iddialar

Bu proje şu iddiaları **yapmayacaktır**:

- Evrenin ontolojik olarak zamansız olduğu;
- Geleceğin fiziksel olarak geçmişi değiştirdiği;
- Retrocausality;
- Quantum advantage veya classical hidden-clock theory’nin genel olarak çürütülmesi;
- GHZ ölçümünün tek başına Page–Wootters clock ambiguity problemini çözmesi;
- Redundant records’ın partition’dan bağımsız unique clock seçtiği;
- Bir LLM ajanının zamanı “deneyimlediği”.

---

# 1. Araştırma soruları ve hipotezler

## RQ1 — Objective clock basis

Sabit bir physical partition altında, en az iki disjoint fragment tarafından redundantly ve nondegenerately kaydedilen candidate clock basis ne ölçüde unique’tir?

### H1

Exact ideal durumda objective basis, admissible partition class içinde outcome permutation ve local phase convention dışında unique olur.

**Konumlandırma:** Bu hipotez ana novelty değildir; Fu’nun redundant-imprint uniqueness sonucunun clock bağlamındaki imported foundation’ı olarak ele alınacaktır.

## RQ2 — Temporal order

Objective basis bilindikten sonra persistent records temporal label’lar üzerinde hangi order’ı operasyonel olarak belirler?

### H2

Binary persistent record signatures `b(t) ∈ {0,1}^m` için gözlenebilir verinin belirlediği maximal temporal relation coordinate-wise dominance’tır:

\[
t \preceq_B t' \iff b_e(t) \le b_e(t') \quad \forall e.
\]

Persistent record’ları silmeden izlenebilen bütün fiziksel trajectories tam olarak `P_B=(T,\preceq_B)` içindeki chains’dir. Poset total değilse bütün label’ları ziyaret eden tek bir scalar timeline yoktur.

## RQ3 — Unique order ve orientation

Hangi koşullarda unique scalar time order elde edilir?

### H3

Unique total order ancak `P_B` total ve antisymmetric ise çıkar. Orientation ancak record states’in “blank → present” semantiği fiziksel olarak anchored ve allowed transformations altında complement/reversal symmetry yasaklanmışsa tanımlanır.

## RQ4 — Record capacity

N adet clock state’i persistent records ile tek bir total order içinde ayırt etmek için minimum record capacity nedir?

### H4

m binary monotone record coordinate, en fazla m+1 uzunluğunda strict chain kodlayabilir. Bu nedenle N unique ordered clock state için:

\[
m \ge N-1.
\]

Bound thermometer code ile tight’tır.

## RQ5 — Gürültü ve redundancy

Independent record noise altında kaç redundant copy order recovery için yeterlidir?

### H5

Her record bit’in q bağımsız kopyası ve bit-error probability `p<1/2` ise majority decoding’in tek bit hata olasılığı Hoeffding ile:

\[
P(\hat b_e \ne b_e) \le \exp[-2q(1/2-p)^2].
\]

Bütün N×m truth-table entry’lerinin en az `1-δ` olasılıkla doğru geri kazanılması için yeterli koşul:

\[
q \ge \frac{\log(Nm/\delta)}{2(1/2-p)^2}.
\]

## RQ6 — Partition no-go

Physical tensor partition sınırsızsa objective clock basis unique kalabilir mi?

### H6

Hayır. Arbitrary global refactorization allowed olduğunda clock factor ve record fragments operasyonel invariant değildir; basis uniqueness ancak fiziksel locality/accessible-algebra ile kısıtlanmış partition class içinde anlamlıdır.

## RQ7 — Quantum illustration

Dört-qubit GHZ history state, redundant objective basis ile global coherent alternative decomposition ayrımını gösterebilir mi?

### H7

GHZ4 için Z-basis clock outcome’ları R1 ve R2’de separately accessible redundant records’a sahiptir; X-basis conditional branch bilgisi tek tek fragments’ta yoktur, global X-parity’de bulunur. Dephased matched control Z objectivity’yi korur fakat global coherence witness’ını yok eder.

---

# 2. Formal model

## 2.1 Static/stationary history representation

“Stationary” kelimesi burada laboratuvar donanımının Hamiltonian altında sürekli stationarity’si anlamına gelmez. Bir history’nin tek bir global state ile, dışarıdan bir runtime index verilmeden temsil edilmesi anlamına gelir.

### Quantum representation

\[
\rho \in \mathcal D(\mathcal H_C\otimes \mathcal H_S\otimes \mathcal H_R),
\qquad
\mathcal H_R=\bigotimes_{j=1}^{m}\mathcal H_{R_j}.
\]

İstenirse Wheeler–DeWitt/Page–Wootters constraint:

\[
K\rho=0 \quad \text{veya} \quad [K,\rho]=0
\]

ayrıca tanımlanabilir; ana order theorem’leri bu constraint’e bağlı değildir.

### Classical representation

\[
P(C,S,R_1,\ldots,R_m)
\]

tek bir joint distribution olarak tutulur. Classical experiments, quantum coherence gerektirmeyen order/redundancy sonuçlarının null ve kontrol dünyasıdır.

## 2.2 Physical partition

Bir partition:

\[
\mathfrak p=(C,S,R_1,\ldots,R_m)
\]

Hilbert-space factorization ve local-access structure’ı birlikte belirtir.

### Admissible partition class `𝔓`

Bir partition yalnızca aşağıdaki koşullardan en az biriyle fiziksel olarak gerekçelendirilmişse admissible kabul edilir:

- spatial locality;
- independently addressable hardware registers;
- fixed accessible operator algebras;
- known subsystem wiring;
- allowed transformations’ın yalnız local unitary/permutation olması.

Arbitrary global unitary refactorization `𝔓` içine alınmaz.

## 2.3 Candidate clock basis

Bir candidate clock basis, C üzerinde rank-1 PVM’dir:

\[
\mathsf T=\{\Pi_t=|t\rangle\langle t|\}_{t\in T}.
\]

### Weak relational admissibility

Outcome t’ye koşullanan world state:

\[
\rho_{W|t}=\frac{\operatorname{Tr}_C[(\Pi_t\otimes I_W)\rho]}{p_t},
\qquad W=S R_1\cdots R_m.
\]

Aday basis en az iki farklı conditional world state üretmelidir.

### Strong relational admissibility — opsiyonel

Bir tek step-channel `𝒰` bulunmalı:

\[
\rho_{W|t+1}=\mathcal U(\rho_{W|t})
\]

belirlenen path veya cycle boyunca. Bu kriter yalnız “full clock” iddiası gereken analizlerde kullanılacaktır. GHZ experiment’te X decomposition, bu kriter raporlanmadan kesin bir full clock olarak adlandırılmayacaktır.

## 2.4 Perfect local record

Fragment `R_j`, t hakkında perfect record taşır iff conditional states’in support’ları pairwise orthogonal’dır:

\[
\rho_{R_j|t}\rho_{R_j|t'}=0,\qquad t\ne t'.
\]

Eşdeğer olarak t’yi sıfır hata ile decode eden bir local POVM vardır.

## 2.5 Approximate record

İki alternatif ölçü kullanılacaktır:

### Helstrom error

Binary durumda:

\[
\epsilon_j^*=\frac12\left(1-\|p_0\rho_{R_j|0}-p_1\rho_{R_j|1}\|_1\right).
\]

### Normalized Holevo information

\[
O_j(\mathsf T)
=
\frac{\chi(T:R_j)}{H(T)},
\]

\[
\chi(T:R_j)=S\!\left(\sum_t p_t\rho_{R_j|t}\right)-\sum_t p_t S(\rho_{R_j|t}).
\]

`O_j=1` perfect locally accessible record, `O_j=0` no locally accessible classical clock information demektir.

## 2.6 Redundancy

`q`-redundant record, q adet disjoint fragment’ın aynı t değişkenini ayrı ayrı decode edebilmesidir.

\[
\mathcal R_\delta(\mathsf T)
=
\#\{j:O_j(\mathsf T)\ge 1-\delta\}.
\]

Primary exact threshold `δ=0`; noisy simulations için `δ∈{0.01,0.05,0.1}` raporlanır.

## 2.7 Independent accessibility ve strong independence

Minimum operasyonel koşul: her observer yalnız tek fragment üzerinde local measurement ile t hakkında bilgi alabilir.

Ideal structural condition:

\[
\rho_{R_1\ldots R_m|t}
=
\bigotimes_j \rho_{R_j|t}.
\]

Approximate condition, conditional total correlation ile ölçülür:

\[
\eta_{\mathrm{ind}}
= D\!\left(\rho_{R_1\ldots R_m|t}
\middle\|
\bigotimes_j\rho_{R_j|t}\right).
\]

Pairwise conditional independence tek başına yeterli kabul edilmeyecektir.

## 2.8 Nondegenerate record

Record signature map injective olmalıdır:

\[
t\ne t' \implies
(\rho_{R_1|t},\ldots,\rho_{R_m|t})
\ne
(\rho_{R_1|t'},\ldots,\rho_{R_m|t'}).
\]

## 2.9 Objective clock basis

Bir basis `𝕋`, partition `𝔭∈𝔓` altında `(q,δ)`-objective iff:

1. q≥2 disjoint fragment vardır;
2. her fragment için `O_j(𝕋)≥1-δ`;
3. local decoding ayrı ayrı yapılabilir;
4. nondegeneracy sağlanır;
5. ideal theorem rejiminde conditional factorization sağlanır.

## 2.10 Basis distance

İki rank-1 PVM arasındaki permutation-invariant distance:

\[
d_{\mathrm{basis}}(\mathsf T,\mathsf T')
=
1-
\max_{\pi\in S_N}
\frac1N\sum_t
\operatorname{Tr}(\Pi_t\Pi'_{\pi(t)}).
\]

0: permutation dışında aynı basis.  
N=2 için orthogonal Bloch axes maksimum ayrıdır.

---

# 3. Persistent records ve temporal order

## 3.1 Event-record coordinates

E adet event type olsun. Her clock label t için ideal persistent record vector:

\[
b(t)=(b_1(t),\ldots,b_E(t))\in\{0,1\}^E.
\]

`b_e(t)=1`, event e’nin persistent record’unun t label’ında mevcut olduğunu ifade eder.

Her coordinate q kez redundantly tutulabilir:

\[
b_{e,1}(t),\ldots,b_{e,q}(t).
\]

## 3.2 Persistence axiom

Bilinmeyen gerçek temporal order `<` altında:

\[
t<t' \implies b_e(t)\le b_e(t') \quad \forall e.
\]

Bu axiom record’un silinmediğini söyler. Record erasure olan sistemler ayrı experiment family’sidir ve order inference için axiom violation olarak işaretlenir.

## 3.3 Blank/present orientation anchor

0 ve 1 salt matematiksel label değildir. Orientation ancak aşağıdaki operational asymmetry önceden tanımlıysa anlamlıdır:

- `0`: calibrated blank memory state;
- `1`: event-coupled written state;
- allowed write channel `0→1`;
- permitted passive dynamics içinde spontaneous `1→0` yok veya ayrı failure olarak gözlenir.

Bu anchor yoksa bit complement + time reversal symmetry orientation’ı belirsiz bırakabilir.

## 3.4 Induced record preorder

\[
t\preceq_B t'
\iff
b_e(t)\le b_e(t')\quad \forall e.
\]

Duplicate signatures varsa preorder çıkar. Eşdeğerlik:

\[
t\sim_B t' \iff b(t)=b(t').
\]

Quotient üzerinde induced relation bir poset’tir.

## 3.5 Persistent trajectories ve branching time

Bir sequence `\gamma=(t_0,\ldots,t_k)` B-persistent iff:

\[
b(t_0)\le b(t_1)\le\cdots\le b(t_k)
\]

coordinate-wise sağlanır.

### Teorem O1 — Chain characterization

B-persistent trajectories tam olarak `P_B` poset’i içindeki chains’dir.

#### Proof obligation

- Persistence sağlayan her sequence’in bütün ardışık ve dolaylı pair’leri coordinate-wise comparable’dır; dolayısıyla bir chain oluşturur.
- Poset içindeki her chain dominance yönünde sıralandığında bütün record bits nondecreasing kalır.

### Corollary O1.1 — Unique scalar timeline

Bütün clock labels tek bir persistent trajectory üzerinde yer alabilir iff `P_B` bir chain/total order’dır. Bu durumda order unique’tir.

### Corollary O1.2 — Branching-time output

`P_B` total değilse doğru çıktı scalar clock değildir. Fiziksel candidate histories, minimal-to-maximal **maximal chains** ile temsil edilir. Incomparable snapshots alternatif branch/cut’lardır; bunları bir linear extension ile zorla sıralamak persistent record silinmesi yaratır.

### Corollary O1.3 — Linear extensions yalnız scheduler totalization’dır

`LinExt(P_B)` order constraints’i ihlal etmeyen topological totalizations verir; fakat consecutive incomparable states arasında record loss olabileceği için genel olarak fiziksel trajectory değildir. Bu nedenle linear-extension count yalnız scheduler/gauge ambiguity diagnostic’i olarak raporlanır.

## 3.6 Residual symmetry

\[
G_B=\operatorname{Aut}(P_B)
\]

record-poset’i koruyan label relabeling grubudur.

Ayrıca:

\[
A_{\mathrm{branch}}=\log |\mathrm{MaxChains}(P_B)|,\qquad A_{\mathrm{lin}}=\log |\mathrm{LinExt}(P_B)|,
\quad
A_{\mathrm{sym}}=\log |G_B|
\]

üç ayrı ambiguity ölçüsüdür. `A_branch` fiziksel persistent branches’i, `A_lin` keyfî topological totalizations’ı, `A_sym` ise label symmetries’i ölçer; bunlar karıştırılmamalıdır.

## 3.7 Temporal order capacity

### Teorem O2 — Binary record capacity

E binary persistent coordinate ile distinct signature’lardan oluşan strict chain’in maksimum uzunluğu E+1’dir.

Bundan:

\[
N\le E+1,
\qquad E\ge N-1.
\]

#### Tight construction — thermometer code

\[
b(t)=
(\underbrace{1,\ldots,1}_{t},
\underbrace{0,\ldots,0}_{N-1-t}),
\quad t=0,\ldots,N-1.
\]

### Teorem O3 — Multi-level record capacity

Coordinate e, `L_e` ordered persistent level alıyorsa product-of-chains içindeki maksimum chain:

\[
N\le 1+\sum_e(L_e-1).
\]

Bu bound experiment design’da minimum physical record capacity hesabı olarak kullanılır.

## 3.8 Noisy redundant records

Her event bit q bağımsız fragment’a kopyalanır. Her copy independent bit-flip error `p<1/2` taşır.

Majority decoder:

\[
\hat b_e(t)=\operatorname{majority}_{k=1}^q b_{e,k}^{\mathrm{obs}}(t).
\]

### Teorem O4 — Sufficient redundancy bound

Per bit:

\[
P(\hat b_e(t)\ne b_e(t))
\le
\exp[-2q(1/2-p)^2].
\]

Bütün N×E code table için union-bound:

\[
P(\hat B=B)
\ge
1-NE\exp[-2q(1/2-p)^2].
\]

`P(\hat B=B)≥1-δ` için yeterli:

\[
q\ge
\frac{\log(NE/\delta)}{2(1/2-p)^2}.
\]

Bu bound conservative’dir; exact binomial tail de raporlanır.

---

# 4. Basis uniqueness ve no-go sınırları

## 4.1 Imported basis-uniqueness result

Fixed admissible partition ve nondegenerate redundant imprints altında observable uniqueness bilinen prior art’tır. Bu çalışmada:

- yeni teorem olarak numaralandırılmayacak;
- `Imported Proposition B0` olarak açıkça işaretlenecek;
- clock-specific yeni delta, order/orientation katmanında kurulacaktır.

## 4.2 No-go N1 — Redundancy label order vermez

Record channels yalnız t label’ını yayınlıyorsa, herhangi bir permutation `π∈S_N` için:

\[
t\mapsto \pi(t),
\quad
r_t^{(j)}\mapsto r_{\pi(t)}^{(j)}
\]

bütün local record fidelities’i korur. Bu nedenle unordered objective basis, temporal order değildir.

## 4.3 No-go N2 — Orientation swap

İki-tick GHZ record state:

\[
|\Psi\rangle=
\frac{|0\rangle_C|0\rangle_{R_1}|0\rangle_{R_2}
+|1\rangle_C|1\rangle_{R_1}|1\rangle_{R_2}}{\sqrt2}
\]

Z basis’i redundantly kaydeder; fakat `0↔1` swap local record statistics’i değiştirmez. Blank/present veya monotone record structure yoksa orientation çıkmaz.

## 4.4 No-go N3 — Unrestricted partition

Arbitrary global Hilbert-space isomorphisms admissible ise subsystem factors ve “local fragment” kavramı invariant değildir. Bu nedenle:

- objective-clock statement her zaman `𝔓` relative olmalıdır;
- partition class experiment öncesi dondurulmalıdır;
- global refactorization ile bulunan alternative records fiziksel objectivity kanıtı sayılmaz.

## 4.5 No-go N4 — One-fragment basis ambiguity

Maximally entangled pair:

\[
|\Phi^+\rangle_{CR}
=
\frac{|00\rangle+|11\rangle}{\sqrt2}
\]

tek fragment ile herhangi bir conjugate basis’te perfect correlation taşır. Bu nedenle tek record, preferred basis seçmek için yeterli değildir. İki veya daha fazla independently accessible fragment gereksinimi temel kontrol olarak kullanılacaktır.

---

# 5. Klasik ve exact computational experiments

## Genel ilke

Klasik deneyler paper’ın bilimsel omurgasıdır. QPU sonucu olmadan çalışmalıdırlar.

## C0 — Theorem property verification

### Amaç

O1–O4 sonuçlarını exhaustive finite examples üzerinde doğrulamak ve implementation bug’larını bulmak.

### Veri üretimi

- `N=2..8`
- `E=1..8`
- bütün binary maps küçük rejimde;
- random maps büyük rejimde;
- thermometer, diamond, degenerate ve disconnected templates.

### Primary checks

- persistent trajectories = chains; linear extensions yalnız scheduler diagnostic;
- unique order iff total poset;
- strict-chain length ≤ E+1;
- generalized capacity bound;
- maximal-chain, linear-extension ve automorphism count ayrımı.

### Definition of Ready

- formal `RecordCode` type implemente;
- persistence predicate implemente;
- exact maximal-chain ve linear-extension counters small N için doğrulanmış;
- fixed seeds config’te.

### Definition of Done

- N≤7 exhaustive property tests sıfır failure;
- her theorem için en az bir positive ve bir boundary fixture;
- counterexample catalog JSON üretilmiş;
- runtime ve state-space raporlanmış.

## C1 — Redundancy selects basis under fixed partition

### State family

N-dimensional generalized broadcast state:

\[
|\Psi_{N,m}\rangle
=
\frac1{\sqrt N}\sum_{t=0}^{N-1}
|t\rangle_C|s_t\rangle_S
\bigotimes_{j=1}^m |t\rangle_{R_j}.
\]

### Controls

- `m=0`: no record;
- `m=1`: maximally entangled single record;
- `m=2,3`: redundant records;
- nonorthogonal record codewords;
- dependent fragments.

### Candidate basis search

N=2:

\[
U(\theta,\phi)=
\begin{pmatrix}
\cos(\theta/2)&-e^{-i\phi}\sin(\theta/2)\\
e^{i\phi}\sin(\theta/2)&\cos(\theta/2)
\end{pmatrix}.
\]

Grid:

- θ: 0..π, 181 point;
- φ: 0..2π, 361 point.

N>2:

- identity/permutation controls;
- 2000 fixed-seed Haar random unitaries;
- local optimization from top 20 seeds.

### Metrics

- `O_min(T)=min_j χ(T:R_j)/H(T)`;
- redundancy count `R_δ`;
- basis distance;
- fragment conditional total correlation.

### Expected results

- m=1: broad/continuous ambiguity;
- m≥2 ideal broadcast: maxima only objective basis orbitinde;
- record overlap/noise: landscape broadens;
- fragment dependence: false objectivity risk.

### DoD

- GHZ/Bell analytic values numerical tolerance `1e-10`;
- basis landscape saved as NetCDF/Parquet;
- all maxima clustered against permutation orbit;
- control failures correctly recovered.

## C2 — Order reconstruction

### Families

1. **Thermometer chain**
   - unique total order.
2. **Diamond/branching**
   - A before B,C; B,C before D;
   - exactly two maximal persistent branches;
   - no scalar trajectory can visit both incomparable middle snapshots without erasing a record.
3. **Degenerate labels**
   - duplicate record vectors;
   - quotient required.
4. **Disconnected evidence**
   - multiple independent chains.
5. **Orientation-free labels**
   - basis records, no persistent semantics.
6. **Erasure/compaction**
   - persistence violation control.

### Outputs

- induced poset;
- Hasse diagram;
- maximal persistent-chain count;
- linear extension count (scheduler diagnostic only);
- automorphism group size;
- unique-order flag;
- orientation-anchor flag.

### DoD

- all hand-computable fixtures exact;
- scalar order never emitted when poset non-total;
- persistence violations separately flagged, not silently ordered;
- GraphML and JSON artifacts generated.

## C3 — Noise and redundancy phase diagram

### Grid

- N∈{4,8}
- E=N-1 thermometer records
- q∈{1,3,5,7,9,11,15}
- p∈{0.00,0.02,0.05,0.10,0.15,0.20,0.25,0.30}
- 10,000 Monte Carlo trials/config
- seeds derived from master seed 20260620.

### Metrics

- exact code-table recovery;
- exact order recovery;
- Kendall tau when a total estimate exists;
- false scalar-order rate;
- empirical bit error;
- exact binomial bound;
- Hoeffding upper bound.

### Primary figure

Order recovery probability vs q for each p, with theorem bound overlay.

### DoD

- empirical error never systematically exceeds exact binomial prediction beyond Monte Carlo CI;
- Hoeffding bound always conservative;
- result table complete and hash-logged;
- no post hoc grid changes.

## C4 — Partition and independence stress tests

### Tests

- one-fragment Bell ambiguity;
- two-fragment GHZ objectivity;
- conditionally dependent fake redundancy;
- fragment regrouping;
- arbitrary global-unitary no-go demonstration;
- nondegenerate vs degenerate imprints.

### Primary outcome

A table stating which assumption fails and which identifiability conclusion becomes invalid.

### DoD

- each theorem assumption has at least one explicit failure fixture;
- no-go examples are minimized by Hilbert dimension/qubit count;
- code and prose counterexamples agree.

## C5 — GHZ exact classical/quantum comparison

### States

\[
\rho_{\mathrm{GHZ}}=|GHZ_4\rangle\langle GHZ_4|,
\]

\[
\rho_{\mathrm{mix}}=
\tfrac12|0000\rangle\langle0000|
+
\tfrac12|1111\rangle\langle1111|.
\]

### Exact expected observables

| Observable | GHZ | dephased mixture |
|---|---:|---:|
| `<Z_C Z_R1>` | 1 | 1 |
| `<Z_C Z_R2>` | 1 | 1 |
| `<X_C X_R1>` | 0 | 0 |
| `<X_C X_R2>` | 0 | 0 |
| `<X_C X_S X_R1 X_R2>` | 1 | 0 |

### Interpretation

- Z records are classical/objective and do not require coherence.
- Global X parity requires coherence.
- Coherence creates a global alternative decomposition, not local objectivity.

---

# 6. Quantum circuit protocol

## 6.1 Qubit map

Logical order, bütün kod ve metadata’da sabit:

| Logical | Qiskit logical index | Role |
|---|---:|---|
| C | 0 | candidate clock subsystem |
| S | 1 | system/world subsystem |
| R1 | 2 | record fragment 1 |
| R2 | 3 | record fragment 2 |

Qiskit bitstring endianness parser unit-test ile doğrulanmadan hiçbir result analiz edilmeyecektir.

## 6.2 Science circuits

### Q-GHZ+

1. `H(C)`
2. `CX(C,S)`
3. `CX(C,R1)`
4. `CX(C,R2)`

### Q-GHZ−

Q-GHZ+ ardından:

5. `Z(C)`

### Measurement variants

- `Z-measure`: direct measurement all qubits.
- `X-measure`: `H` on all qubits, then measurement.

Dört science circuit:

1. GHZ+ / Z
2. GHZ+ / X
3. GHZ− / Z
4. GHZ− / X

Matched dephased control, GHZ+ ve GHZ− distributions’ın 50/50 classical mixture’ıdır. Bu kontrol aynı entangling depth’i korur.

## 6.3 Primary quantum statistics

Shot bit `x_i∈{0,1}` için spin variable:

\[
z_i=(-1)^{x_i}.
\]

### Local objective correlations

\[
C_{Z,1}=\langle Z_C Z_{R_1}\rangle,
\quad
C_{Z,2}=\langle Z_C Z_{R_2}\rangle.
\]

\[
C_{X,1}=\langle X_C X_{R_1}\rangle,
\quad
C_{X,2}=\langle X_C X_{R_2}\rangle.
\]

### Objectivity contrast

\[
\Delta_{\mathrm{obj}}
=
\min(C_{Z,1},C_{Z,2})
-
\max(|C_{X,1}|,|C_{X,2}|).
\]

Ideal: 1.

### Coherence parity

\[
W_{+}=\langle X_C X_S X_{R_1}X_{R_2}\rangle_{GHZ+},
\]

\[
W_{-}=\langle X_C X_S X_{R_1}X_{R_2}\rangle_{GHZ-}.
\]

Ideal `W+=+1`, `W−=-1`.

Matched dephased estimate:

\[
W_{\mathrm{mix}}=\tfrac12(W_++W_-)=0.
\]

### Coherence contrast

\[
\Delta_{\mathrm{coh}}
=|W_+|-|W_{\mathrm{mix}}|.
\]

Ideal: 1.

### Secondary metrics

- measurement mutual information `I(Z_C:Z_Rj)`;
- `I(X_C:X_Rj)`;
- parity success probability;
- raw/mitigated comparison;
- block drift.

## 6.4 Local simulation stages

### Stage Q0 — Statevector

Tolerances:

- pairwise Z correlations: `1±1e-12`;
- pairwise X correlations: `0±1e-12`;
- global X parity: `±1±1e-12`;
- mixture parity: `0±1e-12`.

### Stage Q1 — Generic noise sweep

- 1Q depolarizing: 0..0.005
- 2Q depolarizing: 0..0.03
- readout flip: 0..0.10
- optional T1/T2 grid
- 20,000 shots/grid point for stable design estimates.

### Stage Q2 — Backend-derived digital twin

Backend properties snapshot ile Aer noise model kurulur. En az 20 transpiler seed’i değerlendirilir; selection rule hardware sonuçlarını görmeden uygulanır.
G4 preflight aşamasındaki mevcut Q304 uygulaması, seçili layout üzerindeki
1Q/2Q/readout hata oranlarından türetilmiş aggregate local proxy modelidir.
Tam ISA-circuit/hash freeze ve transpiler-seed seçimi H402'de ayrıca yapılır.

## 6.5 IBM backend-selection rule

QPU seçiminde post hoc cherry-picking yasaktır.

Eligible backends:

- operational;
- Open Plan instance üzerinden accessible;
- dört connected qubit içeren;
- dynamic circuit gerektirmeyen standard gates destekleyen;
- GHZ entangling workload'u için `cx`, `cz` veya `ecr` gibi native iki-qubit
  entangling gate expose eden.

Her candidate layout için deterministic score:

\[
S=5\,\overline e_{2q}
+2\,\overline e_{ro}
+0.01\,D
+0.005\,N_{2q},
\]

burada:

- `e_2q`: selected entangling edges error;
- `e_ro`: selected qubit readout error;
- D: transpiled depth;
- N2q: 2Q gate count.

Lowest score seçilir. Tie-break: backend name, ardından lexicographic physical layout.

## 6.6 Transpilation rule

- Qiskit preset pass manager;
- optimization level 3;
- fixed seeds 0..19;
- chosen layout fixed;
- seed selection: lexicographic minimum `(N2q, depth, estimated_error, seed)`;
- final ISA circuits serialized QPY/QASM3;
- circuit hashes preregistration manifest’e yazılır.

## 6.7 Shot plan

### Science

Dört circuit × dört interleaved block × 1024 shots:

\[
4\times4\times1024=16384.
\]

Circuit order fixed seed ile randomize edilir.

### Readout calibration

Independent assignment approximation:

- her logical/physical qubit için prepare 0 ve 1;
- 8 circuits ×1024 shots =8192.

### Total

24,576 shots, 24 circuit instances.

Bu sayı backend queue/runtime durumuna göre azaltılmayacaktır; Open Plan gate öncesi actual estimated QPU usage kontrol edilir.

## 6.8 Error mitigation policy

Primary result: **raw**.

Secondary result:

- local tensor-product readout assignment correction;
- negative quasi-probabilities varsa clipping yapılmadan hem raw matrix hem corrected estimate raporlanır;
- ZNE/PEC kullanılmaz;
- TREX/advanced mitigation yalnız ayrı exploratory analysis olarak, preregistered primary sonucu değiştirmeden yapılabilir.

## 6.9 Statistical inference

### Correlation confidence intervals

Her ±1 observable için success probability:

\[
p=(1+\langle O\rangle)/2.
\]

Clopper–Pearson interval p üzerinde hesaplanıp expectation interval’a map edilir.

### Nonlinear contrasts

`Δ_obj` ve `Δ_coh` için:

- stratified shot bootstrap;
- 10,000 replicates;
- circuit/block structure korunur;
- percentile ve BCa intervals raporlanır.

### Preregistered hardware inclusion thresholds

Main-text quantum figure için bütün koşullar:

1. `LCB95(Δ_obj_raw)>0.40`
2. `LCB95(min(C_Z1,C_Z2))>0.60`
3. `LCB95(Δ_coh_raw)>0.30`
4. GHZ− parity sign doğru
5. no single block, total effect’in %50’den fazlasını taşımıyor
6. raw ve mitigated sonuçlar qualitatively aynı conclusion’a sahip.

Koşul 1–2 geçer, 3 geçmezse sonuç yalnız classical record objectivity illustration olarak supplement’e gider. Hiçbiri geçmezse hardware sonucu null olarak raporlanır veya paper’dan çıkarılır; teori etkilenmez.

---

# 7. Preregistration ve anti-forking-path kuralları

## QPU’dan önce dondurulacaklar

- logical qubit map;
- exact circuit family;
- backend/layout selection algorithm;
- eligible backend filter;
- transpiler versions ve seed set;
- shot count;
- circuit randomization seed;
- primary endpoints;
- confidence method;
- mitigation policy;
- inclusion thresholds;
- rerun policy;
- failed-job definition;
- bitstring parser tests;
- raw data schema.

## Rerun policy

Rerun yalnızca:

- provider job status failed/cancelled;
- counts eksik;
- circuit manifest mismatch;
- provider-confirmed service incident;
- calibration circuits science circuits ile aynı job/batch’e ulaşmadı.

Scientific result zayıf diye rerun yapılmaz.

## Raw-data immutability

Downloaded provider payload SHA-256 ile hash’lenir ve `results/raw/` altında write-once tutulur.

---

# 8. Sonuç yorumlama karar ağacı

## Outcome A — Theory + hardware positive

- Basis-vs-order theorem’leri doğrulanır.
- GHZ objectivity ve coherence contrasts geçer.
- Paper ana metinde küçük quantum illustration içerir.

Yorum:

> Redundant local records objective clock basis seçebilir; global coherence başka relational decompositions’a izin verse de bunlar local objectivity kazanmaz. Temporal order ise ek persistent record structure gerektirir.

## Outcome B — Theory positive, coherence hardware null

- Main paper theory/classical olur.
- IBM result supplement veya null report.
- Quantum-specific iddia yapılmaz.

## Outcome C — Basis selection classical mixture’da aynı

Beklenen boundary result:

> Objectivity selection mechanism quantum coherence’a ihtiyaç duymaz; coherence yalnız alternative global decomposition space’ini genişletir.

Bu negatif değil, ana sınır sonucudur.

## Outcome D — Order cannot be uniquely recovered

- Eğer induced poset non-total ise scalar time reddedilir.
- Partial order result paper’ın doğruluğunu güçlendirir.

## Outcome E — Robust bound loose but exact theorem survives

- T3/robust section paper’dan çıkarılabilir.
- Exact/order-capacity results korunur.

## Outcome F — Basis theorem tamamen Fu corollary’sine çöker

- Basis theorem “background proposition” yapılır.
- Paper ancak O1–O4 + no-go + experiment package yeterince ayrı bir contribution oluşturuyorsa devam eder.

## Outcome G — Order theorem too elementary and no stronger result emerges

Go/no-go committee paper’ı durdurur. Quantum experiment tek başına publication gerekçesi değildir.

---

# 9. Definition of Ready / Definition of Done

## 9.1 Global Definition of Ready

Uygulamaya başlamadan önce:

- [ ] Research question ve nonclaims bu belgede frozen.
- [ ] `𝔓`, objective basis, record, persistence ve orientation anchor tanımları onaylı.
- [ ] Imported vs novel theorem ayrımı açık.
- [ ] Repo CI ayağa kalkmış.
- [ ] Master seed tanımlı.
- [ ] QPU execution default olarak hard-disabled.

## 9.2 Theory package DoD

- [ ] O1–O4 formal statements LaTeX’te.
- [ ] Her theorem için proof.
- [ ] Her assumption için smallest counterexample.
- [ ] Imported Fu result açıkça cited ve novelty claim’den çıkarılmış.
- [ ] Partition no-go written.
- [ ] Rename test bölümü tamamlanmış.
- [ ] İki bağımsız internal referee proof’u kontrol etmiş.

## 9.3 Classical simulation DoD

- [ ] Bütün exact tests pass.
- [ ] C0–C5 configs immutable.
- [ ] Her result seed/config/code hash içeriyor.
- [ ] Figures scripts ile yeniden üretilebiliyor.
- [ ] Counterexample catalog var.
- [ ] Monte Carlo power/error bars raporlu.

## 9.4 Local quantum DoD

- [ ] Ideal analytic expectations test pass.
- [ ] Endianness tests pass.
- [ ] Generic noise phase diagram tamam.
- [ ] Backend twin simulation tamam.
- [ ] Science thresholds at least one eligible backend modelinde geçiyor.
- [ ] QPY/QASM manifest frozen.

## 9.5 Hardware Definition of Ready

- [ ] `ALLOW_QPU_EXECUTION=YES` explicit.
- [ ] Preregistration mandatory fields complete.
- [ ] Manifest hash match.
- [ ] Open Plan remaining usage checked.
- [ ] Eligible backend/layout selected by frozen rule.
- [ ] All `qpu_gate` tests pass.
- [ ] No uncommitted code changes.

## 9.6 Hardware Definition of Done

- [ ] Job ID stored privately in metadata.
- [ ] Raw provider payload downloaded.
- [ ] SHA-256 manifest generated.
- [ ] No rerun-rule violation.
- [ ] Raw primary analysis executed unchanged.
- [ ] Mitigated secondary analysis separate.
- [ ] Positive/null classification decision tree ile yapılmış.

## 9.7 Research program DoD

- [ ] Theory decision: supported / modified / falsified.
- [ ] Every preregistered experiment complete or documented failure.
- [ ] Positive and negative results interpreted.
- [ ] Claims table updated with evidence grade.
- [ ] Paper go/no-go decision recorded.
- [ ] Reproducibility archive complete.

---

# 10. Evidence grading

Her claim şu sınıflardan biriyle etiketlenecek:

- **P:** proven analytically;
- **E:** exact exhaustive computation;
- **S:** stochastic simulation;
- **Q:** quantum hardware observation;
- **I:** interpretation/inference;
- **N:** negative/no-go result.

Bir cümlede `P` olmayan bir sonuç “prove/show” kelimesiyle yazılmayacaktır.

---

# 11. Figure plan

## Figure 1 — Conceptual hierarchy

Multiple mathematical bases → redundant objective basis → persistent-record poset → unique/partial order.

## Figure 2 — Basis-objectivity landscape

Bell m=1 vs GHZ m=2; Bloch sphere heatmap of `O_min`.

## Figure 3 — Record-capacity theorem

N vs required E; thermometer construction; branching counterexample.

## Figure 4 — Noise/redundancy phase diagram

Exact order recovery vs q,p with theoretical bounds.

## Figure 5 — GHZ coherent vs dephased

Z local correlations, X local correlations, global parity.

## Figure 6 — IBM raw and mitigated

Only if hardware inclusion thresholds pass.

---

# 12. Paper go/no-go after experiments

## Full paper GO

Aşağıdakilerin tamamı:

1. O1–O3 clean theorem/proof;
2. at least one nontrivial capacity or robustness result;
3. fixed-partition basis/objectivity computation;
4. partition/orientation no-go;
5. GHZ ideal/noisy illustration;
6. delete-the-quantum-section test: paper hâlâ meaningful.

## Short theory note GO

- order-poset theorem + record-capacity/no-go güçlü;
- quantum hardware zayıf veya yok.

## ABANDON/PIVOT

- order layer generic order-theory restatement dışında clock-specific insight taşımıyor;
- basis result dışında theorem yok;
- partition assumptions savunulamıyor;
- GHZ experiment standard QD demo’dan hiçbir yeni interpretation ayrımı üretmiyor.

---

# 13. Kaynak omurgası

Bu protokolün teorik sınırlarını belirleyen ana kaynaklar:

1. Riedel, Zurek, Zwolak, *The Objective Past of a Quantum Universe: Redundant Records of Consistent Histories*, arXiv:1312.0331.
2. Hui-Feng Fu, *Uniqueness of the Observable Leaving Redundant Imprints in the Environment in the Context of Quantum Darwinism*, arXiv:2010.14131.
3. Le and Olaya-Castro, *Strong Quantum Darwinism and Strong Independence is equivalent to Spectrum Broadcast Structure*, arXiv:1803.08936; ilgili independence düzeltmeleri ayrıca dikkate alınmalıdır.
4. Bhaskara, Charikar, Vijayaraghavan, *Uniqueness of Tensor Decompositions with Applications to Polynomial Identifiability*, arXiv:1304.8087.
5. Stoica, *The clock ambiguity problem: extended or extinguished?*, arXiv:2604.21805.
6. Zanardi, Lidar, Lloyd, *Quantum tensor product structures are observable-induced*, quant-ph/0308043.
7. Page and Wootters, *Evolution without evolution*, Phys. Rev. D 27, 2885 (1983).

---

# 14. Nihai operasyonel cümle

Bu deney programının başarılı sayılması için “zamanın ne olduğunu” çözmesi gerekmez. Aşağıdaki daha dar ve test edilebilir ayrımı kurması yeterlidir:

> **Redundant records, bir history state içinde hangi clock basis’in çoklu yerel gözlemciler için objektif olduğunu seçebilir; fakat zaman sırası ve yönü, ancak persistent records’ın ek yönlü yapısı tarafından tanımlanır.**

# Claude — Unreal Engine MCP 자동화 저장소

Unreal Engine **5.8** 프로젝트. 에디터를 손으로 조작하는 대신 **MCP(Model Context Protocol) 툴 호출로 제작**한 결과물을 모아둔 저장소입니다. 메시가 필요하면 **Blender MCP**로 만들어 FBX로 넘기고, 레벨 배치·머티리얼·그래프 구성·리깅·검증 캡처까지 전부 코드로 수행합니다.

사용 플러그인: `ModelContextProtocol`, `EditorToolset`, `PCGToolset`, `UMGToolSet`, `AllToolsets`

<table>
<tr>
<td width="25%"><a href="#4-캐릭터-리깅애니메이션"><img src="docs/images/23_char_hero.jpg" width="100%"></a></td>
<td width="25%"><a href="#5-나이아가라-vfx"><img src="docs/images/09_vfx_fire.jpg" width="100%"></a></td>
<td width="25%"><a href="#6-pcg-절차적-숲"><img src="docs/images/01_overview.jpg" width="100%"></a></td>
<td width="25%"><a href="#7-시퀀서-시네마틱"><img src="docs/images/14_seq_pullback.jpg" width="100%"></a></td>
</tr>
<tr>
<td align="center"><b>캐릭터 리깅·애니메이션</b><br>본 20 · 액션 2종</td>
<td align="center"><b>나이아가라 VFX</b><br>시스템 5종 · 에미터 23</td>
<td align="center"><b>PCG 절차적 숲</b><br>인스턴스 70,325</td>
<td align="center"><b>시퀀서 시네마틱</b><br>42초 · 6샷</td>
</tr>
</table>

## 목차

커밋 순서(작업한 순서)대로 정렬했습니다.

| # | 작업 | 규모 | 폴더 | 커밋 |
|---|---|---|---|---|
| [1](#1-한국-구도심-골목) | 한국 구도심 골목 | 에셋 150 / 프롭·모듈러 세트 | `Content/KoreanOldTown` | `30a16b4` `5845a84` |
| [2](#2-산업-항구-모듈러-킷) | 산업 항구 모듈러 킷 | 메시 90 / 텍스처 81 / 액터 1,720 | `Content/IndustrialHarbor_Claude` | `55d1fc5`…`ae3f916` |
| [3](#3-umg-레이아웃-재현) | UMG 레이아웃 재현 | WBP 8종 / 텍스처 15장 | `Content/UIReferenceTest` | `1300782` |
| [4](#4-캐릭터-리깅애니메이션) | **캐릭터 리깅·애니메이션** | 본 20 / 폴리 938 / 액션 2종 | `Content/Characters` | `aa65f26` |
| [5](#5-나이아가라-vfx) | **나이아가라 VFX** | 시스템 5종 / 에미터 23 / 머티리얼 3종 | `Content/VFX_Test` | `5064487` |
| [6](#6-pcg-절차적-숲) | **PCG 절차적 숲** | 그래프 93노드 / 인스턴스 70,325 / 지형 600m | `Content/PCG_Test` | `4cfc69f` |
| [7](#7-시퀀서-시네마틱) | **시퀀서 시네마틱** | 1260프레임 / 6샷 / 카메라 6대 | `Content/VFX_Test` | `1de62e4` |

굵은 항목은 **결과 → 파이프라인 → 재현 방법 → 기술 노트** 순서로 상세 정리했습니다.
기술 노트에는 MCP로 막힌 지점과 우회책을 적어뒀습니다(접혀 있습니다).

---

# 1. 한국 구도심 골목

> `Content/KoreanOldTown`

한국 구도심 상가 골목을 모듈러로 재현한 첫 작업. Blender로 만든 프롭·건물 모듈과 PBR 텍스처를 원본째 저장소(`ExternalAssets/`)에 두고 임포트해 레벨을 구성했습니다.

| 항목 | 값 |
|---|---|
| 언리얼 에셋 | 150 uasset |
| 원본 | PBR 텍스처 + FBX (`ExternalAssets`) |
| 레벨 | 상가 골목 1식 |

---

# 2. 산업 항구 모듈러 킷

> `Content/IndustrialHarbor_Claude`

컨테이너·크레인·창고·배관으로 구성한 산업 항구 킷. 메시 제작부터 머티리얼 인스턴스 파생, 레벨 배치까지 한 파이프라인으로 이었습니다.

| 항목 | 값 |
|---|---|
| Blender 메시 → FBX | 90개 |
| 텍스처 | 81장 (Poly Haven CC0 2K, 압축 설정 적용) |
| 머티리얼 | 마스터 3종 + 인스턴스 56개 |
| 레벨 액터 | 1,720개 |
| 메시 설정 | Nanite 활성 |
| 언리얼 에셋 | 230 uasset |

---

# 3. UMG 레이아웃 재현

> `Content/UIReferenceTest`

참조 UI 스크린샷을 보고 `UMGToolSet`으로 위젯 트리를 구성해 레이아웃을 재현했습니다.

| 항목 | 값 |
|---|---|
| 위젯 블루프린트 | 8종 |
| 텍스처 | 15장 |
| 언리얼 에셋 | 25 uasset |

> 위젯 프로퍼티는 클래스마다 이름이 달라 유추가 안 됩니다. `list_properties` → `get_properties` → `set_properties` 순서를 지키지 않으면 `set_properties`가 조용히 실패합니다.

---

# 4. 캐릭터 리깅·애니메이션

> `Content/Characters` · 소스 `Blender/SK_Character.blend` · `Export/SK_Character.fbx`

참조 이미지 앞/뒤 2장만 놓고 **Blender MCP로 메시 → 리그 → 애니메이션까지 전부 스크립트로 생성**한 뒤 언리얼 스켈레탈 메시로 넘겼습니다. 버텍스를 손으로 찍거나 웨이트를 칠한 곳은 없습니다.

<table>
<tr>
<td width="50%"><img src="docs/images/17_char_front.jpg" width="100%"></td>
<td width="50%"><img src="docs/images/18_char_back.jpg" width="100%"></td>
</tr>
<tr>
<td align="center">정면 — 바이저 · 가슴 코어 · 벨트 버클</td>
<td align="center">후면 — 정수리 스트립 · 등 척추 라인</td>
</tr>
</table>

## 4.1 결과

| 항목 | 값 |
|---|---|
| 메시 | 1,172 verts / 938 polys (언리얼 5,192 verts / 4 섹션) |
| 키 | 180.8 cm (발바닥 z=0 정렬) |
| 본 | 20개 — `root` 최상위 |
| 머티리얼 | 4종 (다크 / 실버 / 오렌지 / 코어 이미시브) |
| `A_Character_Idle` | 60키 / 1.97초 / 30fps |
| `A_Character_Walk` | 24키 / 0.77초 / 30fps |
| 그 외 | Skeleton · PhysicsAsset 자동 생성 |

본 계층은 `root → pelvis → spine → chest → neck → head`, 여기서 `shoulder → upperarm → lowerarm → hand`와 `thigh → calf → foot`이 `_L`/`_R`로 갈라집니다.

## 4.2 파이프라인

메시는 프리미티브를 쌓는 대신 **단면 링을 이어 붙이는 loft**로 만들었습니다. 단면을 초타원(superellipse)으로 두면 지수 하나로 원↔사각을 오갈 수 있어, 같은 코드로 몸통(각진 단면)과 팔다리(둥근 단면)를 뽑습니다.

```
superellipse 링 loft                단면 12~16각, 밴드별 머티리얼 지정
      │
      ├─ ① 몸통·팔·다리            링 시퀀스 + 방향벡터 (팔다리는 축 기울기 반영)
      │    헬멧·코어·벨트·패드·부츠  박스 / 디스크 프리미티브
      │    face_mat(밴드, 세그먼트)   앞·뒤·바깥면 컬러 블로킹
      ├─ ② 아마추어 20본            rest 좌표를 메시 실측값에 맞춰 배치
      ├─ ③ 웨이트                   정점↔본 선분 거리 → 가중치 → 이웃 스무딩
      ├─ ④ 키포즈                   월드축 회전을 본 로컬 쿼터니언으로 변환
      ├─ ⑤ 접지 보정                프레임별 메시 최저점 측정 → pelvis 수직 이동
      └─ ⑥ FBX                      Apply Unit Scale / Bake All Actions / Leaf Bones OFF
```

## 4.3 리깅

자동 웨이트(Bone Heat)는 이 메시에서 **전 정점 웨이트 0**을 냅니다. 파츠가 서로 닫힌 셸이라 열확산 해가 없기 때문입니다. 그래서 정점에서 각 본 선분까지의 거리로 직접 계산했습니다.

```
w = 1 / (거리 + 0.015)^4.2       후보 = 최근접 본 + 그 부모/자식
                                 상위 4개, 임계값 0.02, 이웃 평균 스무딩 1회
```

후보를 최근접 본의 **부모·자식으로만 제한**하는 것이 핵심입니다. 이게 없으면 팔 정점이 가슴 웨이트를 받아 목을 돌릴 때 몸통이 딸려옵니다.

![리깅 검증](docs/images/19_char_rig.jpg)

팔·다리·머리를 동시에 꺾어도 관절이 찢어지지 않고, 어깨 패드·무릎 패드·부츠 같은 별도 파츠도 정확히 따라옵니다.

## 4.4 애니메이션

<table>
<tr>
<td width="50%"><img src="docs/images/20_char_walk.jpg" width="100%"></td>
<td width="50%"><img src="docs/images/21_char_idle.jpg" width="100%"></td>
</tr>
<tr>
<td align="center"><b>Walk</b> — 콘택트 포즈, 뒤꿈치 착지 + 뒷발 밀어내기</td>
<td align="center"><b>Idle</b> — 호흡 + 미세 좌우 흔들림</td>
</tr>
</table>

**Walk** — 24프레임 4키 사이클(contact → down → passing → up)을 반주기만 정의하고 나머지 절반은 좌우 미러로 생성합니다. 팔은 반대쪽 다리와 반대 위상, 골반은 좌우 롤 + 상체 요를 함께 겁니다.

**접지 보정** — 다리를 27° 벌리면 다리 길이가 유지되는 만큼 발이 9cm 뜹니다. 키포즈마다 메시 최저점을 실측해 `pelvis`를 `-min_z`만큼 내리면, 평행이동이라 **1회 보정으로 정확히 수렴**합니다. 키프레임에서 오차 0, 보간 구간 최대 8mm. 이 보정이 골반 상하 바운스(-2.3 ~ +3.1cm)도 자동으로 만들어줍니다.

**Idle** — 60프레임, `chest` 피치로 호흡을 만들고 골반은 수직으로 움직이지 않습니다(발이 뜨지 않게). 위상을 `2π(f-1)/59`로 두어 60프레임이 1프레임과 같아집니다.

## 4.5 언리얼 임포트

![언리얼 임포트 결과](docs/images/22_char_unreal.jpg)

`SkeletalMeshTools.import_file` 한 번으로 SkeletalMesh · Skeleton · PhysicsAsset · AnimSequence 2종 · Material 4종이 생성됩니다. 검증 결과 임포트 경고 0건, 바운드 180.9cm, 정면 +X.

## 4.6 재현

1. 콘텐츠 브라우저에서 `Content/Characters/SK_Character` 열기
2. `A_Character_Walk` / `A_Character_Idle` 더블클릭해 재생
3. 소스를 고치려면 `Blender/SK_Character.blend` → 익스포트 설정은 아래 기술 노트 참고

## 4.7 기술 노트

<details>
<summary><b>MCP로 막힌 것들 — 5건 (펼치기)</b></summary>

**자동 웨이트가 실패합니다.** 파츠를 여러 개의 닫힌 셸로 만들어 join한 메시는 `parent_set(type='ARMATURE_AUTO')`가 "뼈대 히트 웨이팅: 솔루션을 찾지 못 함" 경고와 함께 **전 정점 웨이트 0**을 만듭니다. 버텍스 그룹은 19개 생기는데 값이 전부 비어 있어서, 웨이트가 없다는 걸 눈으로는 못 알아챕니다.
→ **우회**: 거리 기반 수동 웨이트(4.3). 로우폴리에서는 결과가 오히려 예측 가능합니다.

**Blender 좌표가 언리얼에 그대로 갑니다.** `axis_forward='-Z', axis_up='Y'`(기본값)로 내보내면 Blender `(x,y,z)` → 언리얼 `(x,y,z)` 항등 매핑입니다. 언리얼 표준은 +X 정면이므로 **Blender에서 +X를 정면으로 모델링해야** 합니다. +Y 정면으로 만들었다가 90° 틀어진 걸 뒤늦게 발견했습니다(바운드의 `boxExtent.x`가 팔 span으로 잡히면 틀어진 겁니다).
→ **우회**: 메시 정점과 본 rest 좌표를 `(x,y,z) → (y,-x,z)`로 변환. Blender 오른손계 ↔ 언리얼 왼손계 차이 덕에 `_L`/`_R` 라벨도 자동으로 맞습니다. 단 **rest를 돌리면 본 로컬 축이 바뀌어 기존 키가 깨지므로 애니메이션은 재생성**해야 합니다(접지 오차가 8mm → 36mm로 튀는 걸로 드러납니다).

**아마추어 오브젝트 이름이 언리얼 최상위 본이 됩니다.** `armature_nodetype='NULL'`로 둬도 마찬가지입니다. 아마추어 안에 `root` 본을 따로 만들면 `ARM_Character → root → pelvis`로 한 단계 밀립니다.
→ **우회**: 아마추어 **오브젝트** 이름을 `root`로 하고 안쪽 `root` 본은 삭제. 부작용으로 액션 이름이 `SK_X_Anim_root_Idle`이 되므로 임포트 후 `AssetTools.move`로 리네임합니다.

**Blender 5.x 액션에는 `fcurves`가 없습니다.** 슬롯/레이어 구조로 바뀌어 `action.layers[].strips[].channelbags[].fcurves`로 내려가야 합니다. 액션을 붙일 때도 `animation_data.action = act` 다음에 `act.slots.new(id_type='OBJECT', …)` → `animation_data.action_slot = act.slots[0]`까지 해줘야 키가 들어갑니다.

**월드축 회전을 본 로컬로 옮길 때 부모 행렬을 끼우면 안 됩니다.** `bone.matrix_local`은 이미 아마추어 공간 기준이라 `Quaternion(matrix_local.to_3x3().inverted() @ world_axis, angle)`이면 끝입니다. 부모를 한 번 더 곱했더니 다리는 우연히 맞고 팔만 전혀 안 도는 증상이 나왔습니다. 회전을 여러 개 합성할 때는 **나중에 적용할 것을 왼쪽에** 곱합니다(팔을 내린 뒤 앞뒤로 스윙하려면 `q_swing @ q_down`).

**그 외** — 절차적 생성 메시는 UV가 없어 임포트 시 "UV 세트 없음" 경고가 뜹니다. `bpy.ops.uv.smart_project()` 한 줄로 해결됩니다. 그리고 `CaptureAssetImage`/`CaptureEditorImage`는 base64가 커서 응답이 잘리므로, 저장된 tool-results 파일에서 디코드해 PNG로 봐야 합니다.

</details>

---

# 5. 나이아가라 VFX

> `Content/VFX_Test`

나이아가라 시스템 5종을 에디터 UI 없이 만들었습니다. **에미터 23개, 스택 에러 0, 전 시스템 컴파일 UpToDate.** 색·크기 그라데이션은 커브를 쓰지 않고 **HLSL 표현식으로 생성**했습니다 — 커브 DataInterface에 값을 쓰면 에디터가 죽기 때문입니다.

<table>
<tr>
<td width="50%"><img src="docs/images/09_vfx_fire.jpg" width="100%"></td>
<td width="50%"><img src="docs/images/10_vfx_aurora.jpg" width="100%"></td>
</tr>
<tr>
<td><b>NS_Fire</b> — 흰노랑→주황→적색 HDR 램프, 불티, 라이트 렌더러</td>
<td><b>NS_Aurora</b> — 세로 시트 커튼 3겹, 녹색→청록→보라</td>
</tr>
<tr>
<td><img src="docs/images/11_vfx_tornado.jpg" width="100%"></td>
<td><img src="docs/images/12_vfx_water.jpg" width="100%"></td>
</tr>
<tr>
<td><b>NS_Tornado</b> — 반경이 커지는 원통 밴드 5겹 + VortexForce</td>
<td><b>NS_WaterFountain</b> — Velocity-aligned 물줄기, 중력 포물선</td>
</tr>
<tr>
<td><img src="docs/images/13_vfx_lightning.jpg" width="100%"></td>
<td></td>
</tr>
<tr>
<td><b>NS_Lightning</b> — HDR 볼트 + JitterPosition 지그재그, 2.4초 주기 플래시</td>
<td></td>
</tr>
</table>

## 5.1 결과

| 시스템 | 에미터 | 구성 | 핵심 기법 |
|---|---:|---|---|
| NS_Fire | 4 | Core / Embers / Smoke / **Light** | Curl Noise, HDR 램프, 라이트 렌더러 |
| NS_Aurora | 3 | Lower / Mid / Upper | 세로 non-uniform 스프라이트, 초저속 드리프트 |
| NS_Tornado | 7 | Band0–4 / GroundDust / **Debris(Mesh)** | VortexForce, 높이별 반경 확장 |
| NS_WaterFountain | 4 | Jet / Droplets / Mist / Splash | VelocityAligned 스트레치, 중력 −980 |
| NS_Lightning | 5 | MainBolt / Glow / Branch×2 / Sparks | JitterPosition, 시간 게이트 플래시 |
| **합계** | **23** | | |

머티리얼 3종(`M_VFX_Translucent` / `TranslucentRibbon` / `Additive`)은 엔진 기본 나이아가라 머티리얼을 복제해 블렌드 모드만 바꿔 만들었습니다.

## 5.2 파이프라인

모든 스프라이트 에미터가 `Fountain` 템플릿에서 출발해 같은 뼈대를 공유합니다.

```
CreateNiagaraSystem (MinimalLightweight)   시스템 생성 → 템플릿 에미터 제거
      │
      ├─ AddEmitter (Fountain / UpwardMeshBurst)
      │
      ├─ EmitterUpdate   SpawnRate
      ├─ ParticleSpawn   InitializeParticle  수명·크기·색 모드
      │                  ShapeLocation       Cylinder / Cone 분포
      │                  AddVelocity         원뿔 방향 + 속도 범위
      ├─ ParticleUpdate  GravityForce / Drag
      │                  CurlNoiseForce      난류
      │                  VortexForce         회전 (토네이도)
      │                  JitterPosition      각진 변위 (번개)
      │                  ScaleColor          ← HLSL 램프 (RGB·Alpha)
      │                  ScaleSpriteSize     ← HLSL 램프
      │                  SolveForcesAndVelocity
      └─ SetRendererData  머티리얼 / 정렬 / 정렬힌트
                          └ ApplyStackIssueFix 로 솔버 순서 자동 교정
```

`ScaleColor`의 `Scale RGB`·`Scale Alpha`에 중첩 `lerp` 문자열을 넣어 다단 그라데이션을 만듭니다. 불꽃 코어는 이렇게 펼쳐집니다.

```hlsl
lerp(lerp(lerp(float3(12,7,2), float3(8,3.2,0.5),
     saturate((Particles.NormalizedAge - 0.0) * 6.667)),
     float3(3.5,0.9,0.08), saturate((Particles.NormalizedAge - 0.15) * 4.0)), ...)
```

`Particles.NormalizedAge`, `Particles.Position`, `Engine.Time`을 참조할 수 있어 커브보다 표현력이 넓습니다.

## 5.3 재현

1. `Content/VFX_Test/L_VFX_Showcase` 열기
2. 레벨의 `FX_Showcase_*` 액터에서 개별 확인
3. 파티클이 안 보이면 **Simulate**를 켜세요 (에디터 뷰포트는 나이아가라를 tick하지 않습니다)

## 5.4 기술 노트

<details>
<summary><b>MCP로 막힌 것들 — 4건 (펼치기)</b></summary>

**커브 DataInterface에 쓰면 에디터가 크래시합니다.** `ScaleColor.Linear Color Curve` 같은 커브 입력에 `SetStackInputData`를 하면 `PlaceholderDataInterfaceChanged → ResetSystem`이 컴파일 중에 재진입해 `InitDITickLists`에서 널 참조로 죽습니다.
→ **우회**: HLSL 표현식 입력(`NiagaraExt_StackInputData_HlslExpression`)으로 전량 대체. 크래시가 없을 뿐 아니라 표현력도 더 좋습니다.

**`ShapeLocation`의 Box/Plane 셰이프는 파티클이 나오지 않습니다.** Cylinder·Cone은 정상입니다. 오로라가 렌더되지 않던 원인이었고, 원통 분포로 바꾸자 즉시 해결됐습니다. 원뿔은 파티클이 넓은 끝에 몰리므로, 테이퍼 실루엣은 **반경이 커지는 원통 밴드를 쌓는 편**이 예측 가능합니다(토네이도가 그 방식).

**빔(DynamicBeam) 리본은 신뢰할 수 없습니다.** `Use Beam Tangents`의 기본 탄젠트가 0이라 빔이 통째로 붕괴하고, 고쳐도 상대좌표 Start/End가 지정한 길이보다 훨씬 짧게 그려집니다. 오로라·번개 모두 스프라이트 방식으로 선회했습니다.

**그 외 자잘한 것** — `SetEmitterData`는 `bEnabled`가 아니라 **`bIsEnabled`**, 렌더러 프로퍼티는 PascalCase(camelCase는 에러 없이 무시), 스태틱 스위치로 숨겨진 입력은 부모 스위치를 바꿔도 **다음 호출에서 즉시 반영되지 않습니다**.

</details>

---

# 6. PCG 절차적 숲

> `Content/PCG_Test`

규칙만 주면 나무·바위·관목·풀이 알아서 자라는 PCG 그래프. 나무를 한 그루도 손으로 심지 않았고, **지형을 400m에서 600m로 교체했을 때 70,325개가 자동으로 재배치**됐습니다.

![전체 조망](docs/images/01_overview.jpg)

![지상 시점](docs/images/02_road_ground.jpg)

## 6.1 결과

| 레이어 | 메시 | 인스턴스 | 규칙 |
|---|---|---:|---|
| L1 대형 침엽수 | Pine A/B | 2,216 | 고도 1825–6290, 경사 ≤25°, 북사면 선호 |
| L2 중형 활엽수 | Broad A/B, Dead | 5,171 | 고도 100–6290, 경사 ≤30°, 남사면 선호 |
| L3 관목 | Bush A | 25,095 | 활엽수 근접 시에만 (Distance 가중) |
| L4 바위 | Rock A/B/C | 1,386 | 경사 반전 — 급경사일수록 밀집 |
| L5 풀 | Grass A | 31,617 | 고도 ≤5670, 경사 ≤20°, 겹침 허용 |
| L6 저지대 관목 | Bush A | 4,434 | 고도 ≤1690 전담, 밀도 2배 |
| 길 + 자갈 | Road_Segment, Rock A | 406 | 스플라인 추종, 폭 900 내 나무·바위 제거 |
| **합계** | | **70,325** | |

- 그래프 **93 노드 / 101 에지 / 7 브랜치**
- 지형 600m × 600m, 고도 100–9096 유닛
- 서브그래프 `PCG_ScatterLayer` (파라미터 6종) + 재사용 데모 `PCG_BiomeDemo`

## 6.2 파이프라인

모든 브랜치가 같은 6단계 뼈대를 공유하고 숫자만 다릅니다.

```
World Ray Hit Query          지형 표면 획득
      │
      ├─ ① Surface Sampler          격자 후보 포인트
      ├─ ② Normal To Density        경사 → 밀도
      │    Normal To Density        사면 방위(남/북) → 밀도 배수
      │    Spatial Noise (FBM)      펄린 노이즈 → 밀도 (숲 뭉침·빈터)
      │    Filter by Range          고도 컷 (설선 / 저지대)
      │    Distance                 나무까지 거리 → 밀도 (관목 전용)
      ├─ ③ Density Filter           임계값 미만 제거
      │    Self Pruning             최소 간격 이내 제거
      ├─ ④ Transform Points         랜덤 Yaw/스케일/지터 + Z 높이 변조
      ├─ ⑤ Projection               지형 표면에 스냅
      └─ ⑥ Static Mesh Spawner      ISM 인스턴스 생성
                                     └ Difference 로 길 위 제거
```

`$Density`가 기축통화입니다. ②에서 규칙을 밀도에 누적하고 ③에서 실행합니다.

## 6.3 생태 규칙

**설선** — 고도 상한을 넘으면 나무가 사라지고 바위만 남습니다.

![설선](docs/images/03_snowline.jpg)

**경사 편중 + 근접 밀집** — 왼쪽 완경사는 숲, 오른쪽 급사면은 나무 없이 바위. 관목은 나무 주변에만 붙습니다.

![생태 규칙](docs/images/04_ecology.jpg)

**길** — 스플라인을 지형에 투영해 세그먼트 메시를 이어 붙이고, `Difference`로 폭 900 내 나무·바위를 제거합니다. 가장자리엔 풀·관목·자갈이 남습니다.

![길](docs/images/05_road_high.jpg)

**개체 변화** — 같은 메시에 색조가 다른 MaterialInstance를 물려 침엽수 3톤 / 활엽수 3톤으로 갈립니다. Z축만 0.75–1.38배 흔들어 키도 다릅니다.

![색 변화](docs/images/06_color_variants.jpg)

## 6.4 에셋 (Blender MCP 제작)

전부 로우폴리로 스크립트 생성 → FBX → 임포트했습니다. 원본 FBX는 `ImportSource/`에 있습니다.

![Blender 에셋](docs/images/07_blender_assets.jpg)

| 에셋 | 트라이앵글 | 높이 |
|---|---:|---|
| Tree_Pine_A / B | 116 / 94 | 10.1m / 14m |
| Tree_Broad_A / B | 108 / 188 | 8.1m / 11.2m |
| Tree_Dead | 128 | 6.4m |
| Rock_A / B / C | 44 each | 1.1 / 2.0 / 4.2m |
| Bush_A / Grass_A | 80 / 6 | 1.3m / 0.5m |
| Terrain_Forest | 80,802 | 600m, 기복 90m |
| Road_Segment | 40 | 폭 9.2m |

원점은 전부 밑동 바닥 중앙, +Z 업, 트랜스폼 적용 완료 (미터 단위 모델링 → 언리얼에서 1m = 100유닛 정확히 일치).

**접지 검증** — Projection이 정상 동작해 밑동이 뜨거나 묻히지 않습니다.

![접지](docs/images/08_projection.jpg)

## 6.5 재현

1. `Content/PCG_Test/L_PCG_Forest` 열기
2. 아웃라이너에서 `PCG_ForestVolume` 선택
3. Details → PCG Component → **Generate**

파라미터를 바꾸려면 `PCG_ForestGraph`에서 각 브랜치의 `Surface Sampler`(밀도), `Density Filter`(임계값), `Filter by Range`(고도)를 조정합니다. 개수 확인은 노드 우클릭 → **Inspect**.

## 6.6 기술 노트

<details>
<summary><b>MCP로 막힌 것들 — 5건 (펼치기)</b></summary>

**랜드스케이프를 PCG로 샘플링할 수 없습니다.** `Get Landscape Data`가 항상 빈 결과를 냅니다. 원인은 `PCGWorldActor.LandscapeCache`의 `cacheEntryCount`가 0인 것인데, 이 캐시를 빌드하는 경로가 MCP에 없습니다(콘솔 *명령* 실행 툴도 없어 우회 불가). `serializationMode` 변경, 랜드스케이프 더티 마킹, `Wait Until Landscape Is Ready` 삽입 모두 실패했습니다.
→ **우회**: 지형 메시를 `CTF_UseComplexAsSimple` 콜리전으로 두고 `World Ray Hit Query`로 표면을 얻습니다. 노멀도 정상이라 경사 규칙이 전부 동작합니다.

**`Spawn Spline Mesh`는 사용 불가.** 그래프에 넣으면 `ExecuteGraphInstance`가 실패하고, 노드를 지워도 볼륨이 망가진 채 남습니다(볼륨 재스폰으로만 복구). 길은 Static Mesh Spawner로 세그먼트를 이어 붙여 만들었습니다.

**인스턴스별 랜덤 색은 머티리얼 표현식으로 안 됩니다.** `PerInstanceRandom`, `PerInstanceCustomData` 모두 PCG가 만든 ISM에서 값을 못 받습니다(PCG 쪽 어트리뷰트 생성은 정상 확인). descriptor에 `numCustomDataFloats`가 노출되지 않는 것이 원인으로 보입니다.
→ **우회**: `MeshEntries` descriptor의 `OverrideMaterials`로 같은 메시에 색만 다른 MIC를 물립니다.

**그래프 파라미터 → 노드 바인딩은 됩니다.** `Get Graph Parameter` 노드를 만들고 `ConnectNodePins`의 대상 핀 라벨에 **노드 프로퍼티 이름을 그대로** 주면 오버라이드 핀에 연결됩니다(`GetSlopeCos.Out → SlopeCut.LowerBound`). 단 중첩 구조체 프로퍼티(고도 필터의 threshold 등)는 오버라이드 핀이 없어 파라미터화가 안 됩니다.

**튜닝은 실측 분포로.** Density Filter 임계값을 감으로 잡으면 안 됩니다. 노이즈 출력이 0.51–1.0 범위인데 임계값 0.55를 주면 아무것도 안 걸러집니다. `GetNodeDataView`(에디터의 Inspect)로 실제 분포를 읽어 목표 개수의 백분위에서 역산해야 합니다. 그리고 **Self Pruning이 개수의 천장**이라, 샘플을 늘려도 안 늘면 `pointExtents`(= 최소간격 ÷ 2)를 줄이는 것이 유일한 손잡이입니다.

</details>

---

# 7. 시퀀서 시네마틱

> `Content/VFX_Test`

VFX 5종을 훑는 **42초(1260프레임 @ 30fps) 6샷** 시퀀스 `LS_VFX_Showcase`. 샷마다 스포너블 시네카메라를 하나씩 두고 트랜스폼과 **초점거리를 함께 키프레임**했습니다.

![풀백](docs/images/14_seq_pullback.jpg)

## 7.1 샷 구성

| # | 대상 | 구간 | 카메라 워크 | 렌즈 |
|---|---|---|---|---|
| 1 | 오로라 | 0–8s | 좌→우 수평 트래킹 | 16.5mm |
| 2 | 토네이도 | 8–16s | 로우앵글 크레인 업 + 오빗 | 23.5 → 30mm |
| 3 | 번개 | 16–23s | 정지에 가까운 푸시인 | 25.7 → 32.5mm |
| 4 | 분수 | 23–31s | 시계방향 오빗 | 28.3 → 34.6mm |
| 5 | 불 | 31–38s | 클로즈업 회전 | 43.5 → 55.4mm |
| 6 | 풀백 | 38–42s | 상공으로 후퇴, 전체 조망 | 34.6 → 16.5mm |

<table>
<tr>
<td width="50%"><img src="docs/images/15_seq_aurora.jpg" width="100%"></td>
<td width="50%"><img src="docs/images/16_seq_tornado.jpg" width="100%"></td>
</tr>
<tr>
<td>샷 1 — 오로라 (상공 배치, 전 샷의 하늘 배경)</td>
<td>샷 2 — 토네이도 (로우앵글)</td>
</tr>
</table>

오로라는 상공 z=7000에 배치해 **모든 샷의 하늘 배경**으로 쓰고, 나머지는 서로 화면에 겹치지 않도록 X·Y축에 분산했습니다. 초점거리를 키프레임하지 않으면 시네카메라 기본 35mm가 고정되어 풀백 샷에 아무것도 들어오지 않습니다.

## 7.2 재현

1. `Content/VFX_Test/L_VFX_Showcase` 열기
2. 시퀀서에서 `LS_VFX_Showcase` 재생

## 7.3 기술 노트

<details>
<summary><b>MCP로 막힌 것들 — 4건 (펼치기)</b></summary>

**`set_camera_cut_binding`은 항상 실패합니다.** 어떤 ID 형식을 줘도 `call() takes at most 0 arguments`.
→ **우회**: `ObjectTools.set_properties(section, {"CameraBindingID": {"Guid": <bindingId>, "SequenceID": 0, "ResolveParentIndex": 0}})`로 섹션 프로퍼티를 직접 씁니다.

**시퀀서를 연 채 PIE를 시작하면 죽습니다.** `OnPreBeginPIE → OnPlaybackContextChanged → SpawnRegister::CleanUp → DestroySpawnedObject → AActor::Modify`. 레벨에 남은 스폰 카메라도 `ACineCameraActor::Tick`에서 무효 핸들로 죽습니다.
→ 결과적으로 **시퀀서 카메라 뷰는 스크린샷으로 검증할 수 없습니다.** 나이아가라는 시퀀서 재생만으로 충분히 tick하지 않아 화면이 비고, 파티클을 돌리려면 Simulate가 필요한데 그것이 시퀀서와 공존하지 않습니다. 샷 포즈를 좌표로 직접 캡처해 검증했습니다. 실제 영상은 Movie Render Queue가 답입니다.

**노출을 고정하지 않으면 튜닝이 무의미합니다.** 어두운 씬에서 자동 노출이 열려 additive VFX가 전부 흰색으로 포화됩니다. `AutoExposureMethod: AEM_Manual` + Min=Max=1인 언바운드 PostProcessVolume이 필요합니다.

**거리 컬링은 복구되지 않습니다.** Simulate 중 카메라에서 먼 나이아가라는 컬링되어 꺼지는데, 카메라가 돌아와도 되살아나지 않습니다. 여러 이펙트를 한 세션에서 순회 캡처하면 뒤쪽 것이 조용히 빈 화면으로 나옵니다 — 대상마다 Simulate를 다시 시작해야 합니다. 프레임 단위는 tick이 아닌 **display rate** 기준입니다.

</details>

# Tradeable equipment draft — 2026-11-11

Source branch: EquipmentGatesDraft-ChatGPT at 1fc3d59b0807904187fb8e24909e9d6e3b1d920d.
Read-only base: AdvCiv 1.14 at 5970334b64a875b5cdb370c94fc9a98db4eacda6.
Build workflow: dll-build at bf08216b5117a12e2f8ee9282d18fd17fb099f97.

All additions are tagged `XANA: 11-11-2026 Tradeable Equipment for AdvancedCiv`.

## What it does

`TRADE_EQUIPMENT` is a new heading in the diplomacy trade screen, with one row per
equipment piece (name plus the piece's `Button` as icon). It is a one-time item like a
technology: nothing is stored in a `CvDeal` afterwards.

- **Armory.** Each player owns a count per `EquipmentTypes` (`CvPlayer::getEquipmentCount`)
  and a count of pieces carried by units (`getEquipmentInUseCount`). Tradeable pieces are
  owned minus in use. A trade moves one piece from the giver's armory to the receiver's.
- **Rules** (`CvPlayer::canTradeEquipmentTo`, `canPossiblyTradeItem`):
  - the piece has `<bTrade>1</bTrade>`;
  - it is not `bPersonalEquipment`;
  - the giver has a piece that is not in use;
  - the receiver owns none of that type;
  - both teams know a tech with `<bEquipmentTrading>1</bEquipmentTrading>`.
- **AI.** Every player values a piece at `iAITradeValue` gold (converted like gold in
  `AI_dealVal`). An AI refuses to hand over unpriced pieces, refuses its worst enemy and
  anyone at or below its strategic-resource attitude threshold, and keeps its last piece
  of a type from other AIs (a human can negotiate for it). Equipment can balance deals in
  `AI_balanceDeal`, and `AI_doDiplo` proposes equipment deals to humans and AIs on the
  tech-trade contact timer.

## New XML

| File | Tag | Meaning |
|---|---|---|
| `CIV4EquipmentInfos.xml` | `bTrade` | may be offered in diplomacy (default 0) |
| | `iAITradeValue` | AI's price in gold (default 0 = AI won't sell) |
| | `Button` | trade screen icon |
| `CIV4TechInfos.xml` | `bEquipmentTrading` | enables equipment trading (default 0) |
| `CIV4GameText_gamemods_mlp.xml` | `TXT_KEY_TRADE_EQUIPMENT` | heading text |

Placeholders to replace: `bEquipmentTrading` is set on TECH_CURRENCY, the Alicorn Amulet
is priced at 300 gold, and its button is a stock BtS promotion icon.

## Things to know when merging

- Nothing in the DLL puts pieces into an armory yet. Until unit code does, use Python:
  `gc.getPlayer(i).changeEquipmentCount(gc.getInfoTypeForString("EQUIPMENT_ALICORN_AMULET"), 1)`.
- Nothing calls `changeEquipmentInUseCount` yet. `CvPlayer.h` describes the calls unit
  code is expected to make. `CvUnit.cpp/.h` are unchanged.
- `TRADE_EQUIPMENT` is 17, so `TRADE_DISENGAGE` moves from 18 to 19. `CvDeal::read`
  converts older saves (`CvDeal` save flag 1).
- `CvPlayer` save flag is 24 (two armory maps). `CvTeam`'s save format is unchanged; the
  equipment trading count is recounted from known techs on load.
- Tech trading needs the enabling tech on one side only; equipment needs it on both.
  The condition is one line in `CvPlayer::canPossiblyTradeItem`.

## Build composition

The equipment draft does not compile on the pinned base. The commit that carries the
workflow file therefore builds pinned 1.14 plus the trade changes, with these files
differing from the feature commit:

| File | In the build tree |
|---|---|
| `CvUnit.cpp`, `CvUnit.h` | pinned 1.14, no equipment code |
| `CvInfo_Unit.h`, `CvInfo_Unit.cpp` | pinned 1.14 plus a reduced `CvEquipmentInfo` (`isPersonalWeapon`, `isTrade`, `getAITradeValue`) |
| `CvEnumMacros.h` | pinned 1.14 plus the `Equipment` entry only |
| `CvXMLLoadUtilitySet.cpp` | pinned 1.14 plus the `CIV4EquipmentInfos` load call |

Every other source file is identical in both commits. Because `CvUnit.cpp` is the pinned
file in the build tree, `tests/equipment-gates/check.py` only runs at the feature commit
(2c5fc754b3d679dd52b6cfa56a6b50e4d3107a60), not at the build commit. The feature commit keeps the draft's
own versions of the six files above, with the two trade members added to its
`CvEquipmentInfo`.

## Verification

- `python3 tests/equipment-trades/check.py` extracts the four armory/rule functions and
  the two AI functions and runs them against stubs (strict g++ C++03, ASan, UBSan). Passed.
- A clang syntax check in MSVC-compatibility mode passed for all 168 translation units of
  the build tree, Release and Debug. This is not the MSVC 7.1 build and links nothing.
- Not run: the MSVC 7.1 DLL build (result pending from the workflow), XML loading, and
  anything in game. Whether the EXE shows the new heading rests on other mods doing the
  same and has not been observed here.

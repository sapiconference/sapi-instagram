# SAPI Instagram – automatické zverejňovanie carouselov

30 carouselov sa zverejní samo podľa `HARMONOGRAM.md` (utorok a štvrtok o 8:00, od 13. 10. 2026) aj s popiskom, hashtagmi a alt textami. Všetko beží zadarmo cez GitHub Actions a oficiálne Instagram API. Facebook stránka nie je potrebná.

---

## 1. Nahraj repozitár na GitHub (5 min)

1. V Chrome otvor **github.com/new**.
2. Názov: `sapi-instagram`, nastav **Public** (Instagram si obrázky sťahuje z verejnej adresy), klikni **Create repository**.
3. V termináli v rozbalenom priečinku:

```bash
git init
git add .
git commit -m "SAPI carousely"
git branch -M main
git remote add origin https://github.com/TVOJ-UCET/sapi-instagram.git
git push -u origin main
```

---

## 2. Získaj Instagram token (10 – 15 min)

1. V Chrome otvor **developers.facebook.com** a prihlás sa (stačí tvoj osobný Facebook účet).
2. **Moje aplikácie → Vytvoriť aplikáciu.**
3. Prípad použitia: **Spravovať správy a obsah na Instagrame** (*Manage messaging & content on Instagram*). Ak sa pýta na firemné portfólio, zvoľ, že ho teraz nechceš prepojiť.
4. V aplikácii otvor **Instagram → Nastavenie API s prihlásením cez Instagram** (*API setup with Instagram login*).
5. V časti **Generovať prístupové tokeny** klikni **Pridať účet** a prihlás sa do Instagram účtu **SAPI**. Potvrď oprávnenia.
6. Pri účte klikni **Generovať token** a token skopíruj (dlhý reťazec, začína `IG…`).

> Ak Instagram vyžiada potvrdenie testera: v appke Instagram → Nastavenia → Webové povolenia / Aplikácie a weby → Pozvánky testerov → Prijať.
> Aplikácia môže zostať v režime vývoja, pre vlastný účet to stačí.

---

## 3. Vlož tajné kľúče do GitHubu (5 min)

**IG_TOKEN**
1. Repozitár → **Settings → Secrets and variables → Actions → New repository secret**.
2. Name: `IG_TOKEN`, Secret: token z kroku 2 → **Add secret**.

**GH_PAT** (aby si skript vedel token sám obnovovať každý týždeň)
1. GitHub → tvoj profil → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
2. Expiration: **Custom**, dátum aspoň **31. 3. 2027**.
3. Repository access: **Only select repositories → sapi-instagram**.
4. Permissions → Repository permissions → **Secrets: Read and write** → **Generate token** a skopíruj ho.
5. V repozitári pridaj ďalší secret: Name `GH_PAT`, Secret: tento token.

---

## 4. Otestuj (2 min)

1. Repozitár → **Actions** → ak treba, klikni **I understand… enable workflows**.
2. **Zverejňovanie carouselov → Run workflow** → nechaj zaškrtnuté **Testovací beh** → **Run workflow**.
3. V logu musíš vidieť: `Token funguje, účet: @…` a `Obrázky sú dostupné.` Nič sa pritom nezverejní.
4. **Obnova tokenu → Run workflow** → musí skončiť zeleno (`Token obnovený.`).

Hotovo. Prvý carousel vyjde v **utorok 13. 10. 2026 o 8:00** (v praxi do ~20 minút po ôsmej).

---

## Ako to funguje

- Workflow beží každú hodinu. Ak nastal čas niektorého príspevku, zverejní ho a zapíše do `zverejnene.json` – rovnaký carousel sa nikdy nezverejní dvakrát.
- Ak zverejnenie zlyhá, GitHub ti pošle e-mail a skript to skúsi znova o hodinu.
- Token sa každý pondelok automaticky obnoví, takže nevyprší.

## Časté úpravy

- **Zmena dátumu alebo času:** uprav `datum` / `cas` v `harmonogram.json` a pushni.
- **Zmena popisku:** uprav `popisok` v `harmonogram.json`.
- **Pozastavenie:** Actions → Zverejňovanie carouselov → **⋯ → Disable workflow**.

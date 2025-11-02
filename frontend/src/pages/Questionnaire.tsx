import { useEffect, useMemo, useState } from 'react';
import BrandHeader from "../components/BrandHeader";
import walletLogo from "../assets/walletwize.png";

const NEIGHBOURHOODS = ["Ahuntsic-Cartierville",
                        "Anjou",
                        "Baie-D'Urfé",
                        "Beaconsfield",
                        "Boucherville",
                        "Brossard",
                        "Châteauguay",
                        "Côte-des-Neiges",
                        "Côte-Saint-Luc",
                        "Dollard-des-Ormeaux",
                        "Dorval",
                        "Hampstead",
                        "Kahnawake",
                        "Kirkland",
                        "L'Île-Bizard",
                        "L'Île-Dorval",
                        "L'Île-Perrot",
                        "Lachine",
                        "LaSalle",
                        "Laval",
                        "Longueuil",
                        "Mercier-Hochelaga-Maisonneuve",
                        "Mont-Royal",
                        "Montréal-Est",
                        "Montréal-Nord",
                        "Montréal-Ouest",
                        "Notre-Dame-de-Grâce",
                        "Notre-Dame-de-l'Île-Perrot",
                        "Pierrefonds-Roxboro",
                        "Plateau-Mont-Royal",
                        "Pointe-Claire",
                        "Rivière-des-Prairies–Pointe-aux-Trembles",
                        "Rosemont-La Petite-Patrie",
                        "Saint-Lambert",
                        "Saint-Laurent",
                        "Saint-Léonard",
                        "Sainte-Anne-de-Bellevue",
                        "Sainte-Geneviève",
                        "Senneville",
                        "Sud-Ouest",
                        "Verdun",
                        "Ville-Marie",
                        "Villeray–Saint-Michel–Parc-Extension",
                        "Westmount"];
const SCHOOLS = ["McGill",
                 "Concordia",
                 "Université de Montréal",
                 "UQAM",
                 "HEC Montréal",
                 "Polytechnique Montréal"];
const YEARS = ["U0", "U1", "U2", "U3", "U4+"];
const TRANSPORT = ["STM", "Bixi", "Car"];
const EAT_OUT = ["Never", "1-2x/week", "3-5x/week", "Daily"];
const GROCERY_STORES = ["Maxi", "Super C", "Walmart", "Costco", "Metro", "Provigo", "Supermarché P.A.", "Adonis", "IGA",];

type CsvRow = { university: string; program: string; annual_tuition_cad: string };

function parseCSV(text: string): CsvRow[] {
  const lines = text.trim().split(/\r?\n/);
  if (!lines.length) return [];
  const header = lines[0].split(",").map(h => h.trim());
  const idxU = header.indexOf("university");
  const idxP = header.indexOf("program");
  const idxT = header.indexOf("annual_tuition_cad");
  if (idxU < 0 || idxP < 0 || idxT < 0) return [];

  // NOTE: our fields don't contain commas, so a basic split works.
  return lines.slice(1).map(line => {
    const cols = line.split(",").map(c => c.trim());
    return {
      university: cols[idxU] ?? "",
      program: cols[idxP] ?? "",
      annual_tuition_cad: cols[idxT] ?? "",
    };
  }).filter(r => r.university && r.program);
}

export default function Questionnaire() {
  /** --- form state --- */
  const [isStudent, setIsStudent] = useState("Yes");
  const [school, setSchool] = useState<string>(SCHOOLS[0]);
  const [program, setProgram] = useState<string>("");
  const [year, setYear] = useState<string>(YEARS[0]);
  const [groceryStore, setGroceryStore] = useState<string>(GROCERY_STORES[0]);


  const [housingType, setHousingType] = useState("With parents");

  /** --- CSV rows & status --- */
  const [rows, setRows] = useState<CsvRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  // fetch CSV once
  useEffect(() => {
  let cancelled = false;

  (async () => {
    try {
      setLoading(true);
      setErr(null);

      const res = await fetch("/montreal_tuition_annual_cad.csv", { cache: "no-store" });
      if (!res.ok) throw new Error(`CSV HTTP ${res.status}`);

      const text = await res.text();
      const parsed = parseCSV(text);
      if (!parsed.length) throw new Error("CSV empty or wrong headers");

      if (!cancelled) setRows(parsed);
    } catch (e: any) {
      if (!cancelled) setErr(e?.message ?? "Failed to load CSV");
    } finally {
      if (!cancelled) setLoading(false);
    }
  })();

  return () => { cancelled = true; };
 }, []);

  // build { school -> [programs] }
  const programsBySchool = useMemo(() => {
    const map = new Map<string, Set<string>>();
    for (const r of rows) {
      const uni = r.university.trim();
      const prog = r.program.trim();
      if (!map.has(uni)) map.set(uni, new Set());
      map.get(uni)!.add(prog);
    }
    const obj: Record<string, string[]> = {};
    for (const [k, set] of map.entries()) obj[k] = Array.from(set).sort();
    return obj;
  }, [rows]);

  const programOptions = programsBySchool[school] ?? [];

  // reset program whenever school changes
  useEffect(() => { setProgram(""); }, [school]);

  /** ---- styles ---- */
  const field  = "border rounded-lg px-4 py-3 text-lg leading-tight focus:outline-none focus:ring-2 focus:ring-indigo-500";
  const select = `${field} bg-white`;

  // reset program whenever school changes
  useEffect(() => { setProgram(""); }, [school]);


return (
    <div className="min-h-screen bg-white">
        <BrandHeader
            product="WalletWize"
            subtitle="User Questionnaire"
            logoSrc={walletLogo}
            showDivider={true}
        />
        <main className="max-w-5xl mx-auto px-6 py-10 space-y-8">

        {/* BASIC INFORMATION */}
        <section className="grid md:grid-cols-2 gap-6">
          <label className="flex flex-col gap-1">
            <span className="text-sm text-slate-600">Full name</span>
            <input className={field} placeholder="First Last" />
          </label>
          <label className="flex flex-col gap-1">
            <span className="text-sm text-slate-600">Address</span>
            <input className={field} placeholder="123 Rue Sherbrooke O" />
          </label>
        </section>

        {/* STUDENT PROFILE */}
        <section className="grid md:grid-cols-3 gap-6">
          <label className="flex flex-col gap-1">
            <span className="text-sm text-slate-600">Are you a student?</span>
            <select className={select} value={isStudent} onChange={e=>setIsStudent(e.target.value)}>
              <option>Yes</option><option>No</option>
            </select>
          </label>

          {isStudent === "Yes" && (
            <>
              <label className="flex flex-col gap-1">
                <span className="text-sm text-slate-600">School</span>
                <select className={select} value={school} onChange={e=>setSchool(e.target.value)}>
                  {SCHOOLS.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </label>

              <label className="flex flex-col gap-1">
                <span className="text-sm text-slate-600">Year of study</span>
                <select className={select} value={year} onChange={e=>setYear(e.target.value)}>
                  {YEARS.map(y => <option key={y} value={y}>{y}</option>)}
                </select>
              </label>

              <label className="md:col-span-3 flex flex-col gap-1">
                <span className="text-sm text-slate-600">
                  Faculty / Program {loading ? "(loading…)" : err ? `(error: ${err})` : ""}
                </span>
                <select
                  className={select}
                  value={program}
                  onChange={e=>setProgram(e.target.value)}
                  disabled={loading || !!err || programOptions.length === 0}
                >
                  <option value="">
                    {programOptions.length ? "Select program" : "No programs found for this school"}
                  </option>
                  {programOptions.map(p => <option key={p} value={p}>{p}</option>)}
                </select>
              </label>
            </>
          )}
        </section>

        {/* HOUSING */}
        <section className="grid md:grid-cols-2 gap-4">
          <label className="flex flex-col gap-1">
            <span className="text-sm text-slate-600">Neighbourhood</span>
            <select className={select}>
              {NEIGHBOURHOODS.map(n => <option key={n}>{n}</option>)}
            </select>
          </label>
          <label className="flex flex-col gap-1">
            <span className="text-sm text-slate-600">Housing type</span>
            <select className={select} value={housingType} onChange={e=>setHousingType(e.target.value)}>
              <option>With parents</option><option>Rental</option><option>Residence</option><option>Other</option>
            </select>
          </label>
          {["Rental","Residence"].includes(housingType) && (
            <label className="md:col-span-2 flex flex-col gap-1">
              <span className="text-sm text-slate-600">Monthly rent (CAD)</span>
              <input type="number" className={field} placeholder="900" />
            </label>
          )}
        </section>

        {/* TRANSPORT & FOOD */}
        <section className="grid md:grid-cols-2 gap-4">
          <label className="flex flex-col gap-1">
            <span className="text-sm text-slate-600">Transport mode</span>
            <select className={select}>
              {TRANSPORT.map(t => <option key={t}>{t}</option>)}
            </select>
          </label>
          <label className="flex flex-col gap-1">
            <span className="text-sm text-slate-600">Eating out frequency</span>
            <select className={select}>
              {EAT_OUT.map(f => <option key={f}>{f}</option>)}
            </select>
          </label>
          <label className="flex flex-col gap-1">
            <span className="text-sm text-slate-600">Grocery store most frequently visited</span>
            <select
                className={select}
                value={groceryStore}
                onChange={(e) => setGroceryStore(e.target.value)}>
                    
                    {GROCERY_STORES.map((s) => (
                        <option key={s} value={s}>{s}</option>
                    ))}
            </select>
        </label>
          <label className="flex flex-col gap-1">
            <span className="text-sm text-slate-600">Grocery budget per week (CAD)</span>
            <input type="number" className={field} placeholder="60" />
          </label>
        </section>

        <div>
            <button
                type="button"
                className="
                    bg-[#574fa9] hover:bg-[#4e4698] active:bg-[#463f8c]
                    text-white px-6 py-3 text-lg font-semibold
                    tracking-wider
                    rounded-xl shadow
                    focus:outline-none focus:ring-2 focus:ring-[#574fa9]/40
                    transition-colors
                    "
            >
                Generate My Budget Tracker
        </button>
        </div>
      </main>
    </div>
  );
}
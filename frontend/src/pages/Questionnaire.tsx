import { useEffect, useMemo, useState } from "react";
import { APILoader, PlacePicker } from "@googlemaps/extended-component-library/react";

import BrandHeader from "../components/BrandHeader";
import walletLogo from "../assets/walletwize.png";

const apiKey = import.meta.env.VITE_API_KEY as string;

const NEIGHBOURHOODS = [
  "Ahuntsic-Cartierville", "Anjou", "Baie-D'Urfé", "Beaconsfield", "Boucherville",
  "Brossard", "Châteauguay", "Côte-des-Neiges", "Côte-Saint-Luc", "Dollard-des-Ormeaux",
  "Dorval", "Hampstead", "Kahnawake", "Kirkland", "L'Île-Bizard", "L'Île-Dorval",
  "Lachine", "LaSalle", "Laval", "Longueuil", "Mercier-Hochelaga-Maisonneuve",
  "Mont-Royal", "Montréal-Est", "Montréal-Nord", "Montréal-Ouest", "Notre-Dame-de-Grâce",
  "Notre-Dame-de-l'Île-Perrot", "Pierrefonds-Roxboro", "Plateau-Mont-Royal", "Pointe-Claire",
  "Rivière-des-Prairies–Pointe-aux-Trembles", "Rosemont-La Petite-Patrie", "Saint-Lambert",
  "Saint-Laurent", "Saint-Léonard", "Sainte-Anne-de-Bellevue", "Sainte-Geneviève", "Senneville",
  "Sud-Ouest", "Verdun", "Ville-Marie", "Villeray–Saint-Michel–Parc-Extension", "Westmount",
];

const SCHOOLS = [
  // match the display style from the styled branch (short names)
  "McGill", "Concordia", "Université de Montréal", "UQAM", "HEC Montréal", "Polytechnique Montréal",
];

const YEARS = ["U0", "U1", "U2", "U3", "U4+"];
const TRANSPORT = ["STM", "Bixi", "Car"];
const EAT_OUT = ["Never", "1-2x/week", "3-5x/week", "Daily"];
const GROCERY_STORES = ["Maxi", "Super C", "Walmart", "Costco", "Metro", "Provigo", "Supermarché P.A.", "Adonis", "IGA"];

type CsvRow = { university: string; program: string; annual_tuition_cad: string };

function parseCSV(text: string): CsvRow[] {
  const lines = text.trim().split(/\r?\n/);
  if (!lines.length) return [];
  const header = lines[0].split(",").map((h) => h.trim());
  const idxU = header.indexOf("university");
  const idxP = header.indexOf("program");
  const idxT = header.indexOf("annual_tuition_cad");
  if (idxU < 0 || idxP < 0 || idxT < 0) return [];
  return lines
    .slice(1)
    .map((line) => {
      const cols = line.split(",").map((c) => c.trim());
      return {
        university: cols[idxU] ?? "",
        program: cols[idxP] ?? "",
        annual_tuition_cad: cols[idxT] ?? "",
      };
    })
    .filter((r) => r.university && r.program);
}

/** Outer component keeps the Google API loader just like your api branch */
export default function Questionnaire() {
  
    if (!apiKey) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <p className="text-red-500">
          VITE_API_KEY is not defined. Please add it to your .env (VITE_API_KEY=...).
        </p>
      </div>
    );
  }
  return (
    <APILoader apiKey={apiKey}>
      <QuestionnaireForm />
    </APILoader>
  );
}

function QuestionnaireForm() {
  /** ---- state from styled branch ---- */
  const [isStudent, setIsStudent] = useState("Yes");
  const [school, setSchool] = useState<string>(SCHOOLS[0]);
  const [program, setProgram] = useState<string>("");
  const [year, setYear] = useState<string>(YEARS[0]);
  const [groceryStore, setGroceryStore] = useState<string>(GROCERY_STORES[0]);

  const [housingType, setHousingType] = useState("With parents");

  /** ---- CSV rows & loaders ---- */
  const [rows, setRows] = useState<CsvRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        setLoading(true);
        setErr(null);
        // same relative path as styled branch
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
    return () => {
      cancelled = true;
    };
  }, []);

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
  useEffect(() => { setProgram(""); }, [school]);

  /** ---- API branch logic that we keep ---- */
  const [address, setAddress] = useState("");
  const [error, setError] = useState("");

  /** ---- styles to match realfrontendquestionnaire ---- */
  const field =
    "w-full rounded-xl border border-slate-300 px-4 py-3 text-lg " +
    "leading-tight bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500";
  const select = `${field} bg-white`;
  const label  = "text-[13px] uppercase tracking-wide text-slate-600";

  /** ---- submit handler (same Flask POST) ---- */
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;

    const selectedSchool = (form.elements.namedItem("school") as HTMLSelectElement)?.value;
    const selectedYear = (form.elements.namedItem("year") as HTMLSelectElement)?.value;
    const selectedTransport = (form.elements.namedItem("transport") as HTMLSelectElement)?.value;
    const selectedEatOut = (form.elements.namedItem("eat_out") as HTMLSelectElement)?.value;
    const selectedName = (form.elements.namedItem("name") as HTMLInputElement)?.value;
    const selectedProgram = (form.elements.namedItem("program") as HTMLSelectElement)?.value;
    const selectedNeighbourhood = (form.elements.namedItem("neighbourhood") as HTMLSelectElement)?.value;
    const selectedGroceryStore = (form.elements.namedItem("grocery_store") as HTMLSelectElement)?.value;
    const selectedGroceryBudget = (form.elements.namedItem("grocery_budget") as HTMLInputElement)?.value;

    setError("");
    try {
      const res = await fetch("http://127.0.0.1:5000/user_info", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: selectedName,
          address,
          school: selectedSchool,
          year: selectedYear,
          program: selectedProgram,
          neighbourhood: selectedNeighbourhood,
          housingType,
          transport: selectedTransport,
          eat_out: selectedEatOut,
          grocery_stores: selectedGroceryStore,
          grocery_budget: selectedGroceryBudget,
        }),
      });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${res.status}`);
      }
      // const data = await res.json();
      // console.log("Response from flask", data);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
  <div className="min-h-screen bg-[#E9E6FF]">
    {/* If you already render BrandHeader higher up, keep that and remove this */}
    <BrandHeader
      product="WalletWize"
      subtitle="User Questionnaire"
      logoSrc={walletLogo}
    />

    <main className="max-w-5xl mx-auto px-6 py-10">
      {/* ---- Card wrapper (Step 2) ---- */}
      <div className="rounded-2xl bg-white/90 backdrop-blur border border-slate-200/80 shadow-lg p-8 md:p-10">
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* BASIC INFORMATION */}
          <section className="grid md:grid-cols-2 gap-4">
            <label className="flex flex-col gap-1">
              <span className="text-sm text-slate-600">Full name</span>
              <input
                name="name"
                className="border rounded px-3 py-2"
                placeholder="First Last"
              />
            </label>

            <label className="flex flex-col gap-1">
              <span className="text-sm text-slate-600">Address</span>
              <PlacePicker
                placeholder="123 Rue Sherbrooke O"
                country={["ca"]}
                className="border rounded px-3 py-2"
                onInput={(e: any) => setAddress(e.target.value)}
                onPlaceChange={async (e: any) => {
                  const place = e.detail;
                  if (!place) return;
                  await place.fetchFields({ fields: ["formattedAddress", "name"] });
                  setAddress(place.formattedAddress || place.name || "");
                }}
              />
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
              <select name="neighbourhood" className="border rounded px-3 py-2">
                {NEIGHBOURHOODS.map((n) => (
                  <option key={n}>{n}</option>
                ))}
              </select>
            </label>

            <label className="flex flex-col gap-1">
              <span className="text-sm text-slate-600">Housing type</span>
              <select
                className="border rounded px-3 py-2"
                value={housingType}
                onChange={(e) => setHousingType(e.target.value)}
              >
                <option>With parents</option>
                <option>Rental</option>
                <option>Residence</option>
              </select>
            </label>

            {["Rental", "Residence"].includes(housingType) && (
              <label className="md:col-span-2 flex flex-col gap-1">
                <span className="text-sm text-slate-600">Monthly rent (CAD)</span>
                <input
                  type="number"
                  className="border rounded px-3 py-2"
                  placeholder="900"
                />
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

          <button
            type="submit"
            className="mt-2 inline-flex items-center rounded-xl bg-[#574fa9] text-white px-6 py-3 text-lg font-semibold tracking-wider shadow hover:bg-[#4e4698] active:bg-[#463f8c] focus:outline-none focus:ring-2 focus:ring-[#574fa9]/40 transition-colors w-full sm:w-auto"
          >
            Generate My Budget Tracker
          </button>
        </form>

        {error && <p className="mt-4 text-rose-600">{error}</p>}
      </div>
    </main>
  </div>
);
}



// OLD FILE: Questionnaire Form that uses API from Google Maps for Address but Incorrect UI Styling
// import { useState, useRef, useEffect} from 'react';
// //import { APIProvider, useMapsLibrary } from '@vis.gl/react-google-maps';
// import { APILoader, PlacePicker } from '@googlemaps/extended-component-library/react';

// const apiKey = import.meta.env.VITE_API_KEY as string;

// const NEIGHBOURHOODS = ["Ahuntsic-Cartierville",
//                         "Anjou",
//                         "Baie-D'Urfé",
//                         "Beaconsfield",
//                         "Boucherville",
//                         "Brossard",
//                         "Châteauguay",
//                         "Côte-des-Neiges",
//                         "Côte-Saint-Luc",
//                         "Dollard-des-Ormeaux",
//                         "Dorval",
//                         "Hampstead",
//                         "Kahnawake",
//                         "Kirkland",
//                         "L'Île-Bizard",
//                         "L'Île-Dorval",
//                         "Lachine",
//                         "LaSalle",
//                         "Laval",
//                         "Longueuil",
//                         "Mercier-Hochelaga-Maisonneuve",
//                         "Mont-Royal",
//                         "Montréal-Est",
//                         "Montréal-Nord",
//                         "Montréal-Ouest",
//                         "Notre-Dame-de-Grâce",
//                         "Notre-Dame-de-l'Île-Perrot",
//                         "Pierrefonds-Roxboro",
//                         "Plateau-Mont-Royal",
//                         "Pointe-Claire",
//                         "Rivière-des-Prairies–Pointe-aux-Trembles",
//                         "Rosemont-La Petite-Patrie",
//                         "Saint-Lambert",
//                         "Saint-Laurent",
//                         "Saint-Léonard",
//                         "Sainte-Anne-de-Bellevue",
//                         "Sainte-Geneviève",
//                         "Senneville",
//                         "Sud-Ouest",
//                         "Verdun",
//                         "Ville-Marie",
//                         "Villeray–Saint-Michel–Parc-Extension",
//                         "Westmount"];
// const SCHOOLS = ["McGill University",
//                  "Concordia University",
//                  "Université de Montréal",
//                  "UQAM",
//                  "HEC Montréal",
//                  "École Polytechnique de Montréal"];
// const YEARS = ["U0", "U1", "U2", "U3", "U4+"];
// const TRANSPORT = ["STM", "Bixi", "Car"];
// const EAT_OUT = ["Never", "1-2x/week", "3-5x/week", "Daily"];

// export default function Questionaire(){
//     if (!apiKey) {
//         return (
//             <div className="max-w-4xl mx-auto p-6">
//                 <p className="text-red-500">
//                     VITE_API_KEY is not defined. Please check your .env file.
//                 </p>
//             </div>
//         );
//     }
//     return (
//         <APILoader apiKey={apiKey}>
//             <QuestionnaireForm />
//         </APILoader>
//     );
// }

// function QuestionnaireForm() {
    
//     const [isStudent, setIsStudent] = useState("Yes");
//     const [housingType, setHousingType] = useState("With parents");
//     const [error, setError] = useState('');

//     const [address, setAddress] = useState('');
//     //for google address autocomplete
    
    

//     const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
//         e.preventDefault();
//         const form = e.currentTarget;
//         const selectedSchool = (form.elements.namedItem("school") as HTMLSelectElement)?.value;
//         console.log(selectedSchool);
//         const selectedYear = (form.elements.namedItem('year') as HTMLSelectElement).value;
//         console.log(selectedYear);
//         const selectedTransport = (form.elements.namedItem('transport') as HTMLSelectElement).value;
//         console.log(selectedTransport)
//         const selectedEat_out = (form.elements.namedItem('eat_out') as HTMLSelectElement).value;
//         console.log(selectedEat_out);
//         console.log(housingType);
//         console.log(isStudent);
//         const selectedName = (form.elements.namedItem("name") as HTMLInputElement).value;
//         console.log(selectedName);
//         //const selectedAddress = (form.elements.namedItem("address") as HTMLSelectElement).value;
//         //console.log(selectedAddress);
//         console.log(address)
//         const selectedProgram = (form.elements.namedItem("program") as HTMLSelectElement).value;
//         console.log(selectedProgram);
//         const selectedNeighbourhood = (form.elements.namedItem("neighbourhood") as HTMLSelectElement)?.value;
//         console.log(selectedNeighbourhood);
//         const selectedGroceries = (form.elements.namedItem("grocery_stores") as HTMLInputElement)?.value;
//         console.log(selectedGroceries);
//         const selectedGrocery_budget = (form.elements.namedItem("grocery_budget") as HTMLInputElement)?.value;
//         console.log(selectedGrocery_budget);

//         setError('')
//         try {
//             const res = await fetch(
//                 'http://127.0.0.1:5000/user_info', {
//                 method: 'POST',
//                 headers: {'Content-Type': 'application/json'},
//                 body: JSON.stringify({
//                     name : selectedName,
//                     address : address,
//                     school : selectedSchool,
//                     year : selectedYear,
//                     program : selectedProgram,
//                     neighbourhood : selectedNeighbourhood,
//                     housingType : housingType,
//                     transport : selectedTransport,
//                     eat_out : selectedEat_out,
//                     grocery_stores : selectedGroceries,
//                     grocery_budget: selectedGrocery_budget
//                 })
//                 }
//             )

//             if (!res.ok) {
//                 const errorData = await res.json().catch(() => ({}));
//                 throw new Error(errorData.message || `HTTP ${res.status}`)
//             }
//             // const data = await res.json();
//             // console.log('Response from flask', data)

//         } catch (err: any) {
//             setError(err.message)
//         }

//     }

//     return (
    
//         <div className="max-w-4xl mx-auto p-6 space-y-6">
//             <form onSubmit={handleSubmit}>
//                 <h1 className="text-3xl font-bold">Metrix — Student Questionnaire</h1>

//                 {/* Basic */}
//                 <section className="grid md:grid-cols-2 gap-4">
//                     <label className="flex flex-col gap-1">
//                         <span className="text-sm text-slate-600">Full name</span>
//                         <input name='name' className="border rounded px-3 py-2" placeholder="First Last" />
//                     </label>
//                     <label className="flex flex-col gap-1">
//                         <span className="text-sm text-slate-600">Address</span>
//                         {/* <input ref={addressInputRef} name='address' autoComplete="off" className="border rounded px-3 py-2" placeholder="123 Rue Sherbrooke O" /> */}
//                         <PlacePicker
//                             placeholder="123 Rue Sherbrooke O"
//                             country={["ca"]}
//                             className="border rounded px-3 py-2"
//                             onInput={(e: any) => setAddress(e.target.value)}
//                             // FIX: Make the handler async to await the data
//                             onPlaceChange={async (e: any) => {
//                                 const place = e.detail //e.detail; // This is the Place stub
//                                 //e.get_place()
//                                 if (!place) {
//                                     return;
//                                 }

//                                 await place.fetchFields({
//                                     fields: ['formattedAddress', 'name']
//                                 });

//                                 setAddress(place.formattedAddress || place.name || '');
//                             }}
//                         />
//                     </label>
//                 </section>

//                 {/* Student */}
//                 <section className="grid md:grid-cols-3 gap-4">
//                     <label className="flex flex-col gap-1">
//                         <span className="text-sm text-slate-600">Are you a student?</span>
//                         <select className="border rounded px-3 py-2" value={isStudent} onChange={e=>setIsStudent(e.target.value)}>
//                             <option>Yes</option><option>No</option>
//                         </select>
//                     </label>
                    
//                     {isStudent === "Yes" && (
//                         <>
//                             <label className="flex flex-col gap-1">
//                                 <span className="text-sm text-slate-600">School</span>
//                                 <select name='school' className="border rounded px-3 py-2">
//                                     {SCHOOLS.map(s => <option key={s}>{s}</option>)}
//                                 </select>
//                             </label>
//                             <label className="flex flex-col gap-1">
//                                 <span className="text-sm text-slate-600">Year of study</span>
//                                 <select name='year' className="border rounded px-3 py-2">
//                                     {YEARS.map(y => <option key={y}>{y}</option>)}
//                                 </select>
//                             </label>
//                             {/* Program dropdown will depend on school; wire it next */}
//                             <label className="md:col-span-3 flex flex-col gap-1">
//                                 <span className="text-sm text-slate-600">Faculty / Program</span>
//                                 <select name='program' className="border rounded px-3 py-2"><option>Select program</option></select>
//                             </label>
//                         </>
//                     )}
//                 </section>

//                 {/* Housing */}
//                 <section className="grid md:grid-cols-2 gap-4">
//                     <label className="flex flex-col gap-1">
//                         <span className="text-sm text-slate-600">Neighbourhood</span>
//                         <select name='neighbourhood' className="border rounded px-3 py-2">
//                             {NEIGHBOURHOODS.map(n => <option key={n}>{n}</option>)}
//                         </select>
//                     </label>
//                     <label className="flex flex-col gap-1">
//                         <span className="text-sm text-slate-600">Housing type</span>
//                         <select className="border rounded px-3 py-2" value={housingType} onChange={e=>setHousingType(e.target.value)}>
//                             <option>With parents</option>
//                             <option>Rental</option>
//                             <option>Residence</option>
//                         </select>
//                     </label>

//                     {["Rental","Residence"].includes(housingType) && (
//                         <label className="md:col-span-2 flex flex-col gap-1">
//                             <span className="text-sm text-slate-600">Monthly rent (CAD)</span>
//                             <input type="number" className="border rounded px-3 py-2" placeholder="900" />
//                         </label>
//                     )}

//                 </section>

//                 {/* Transportation & Food */}
//                 <section className="grid md:grid-cols-2 gap-4">
//                     <label className="flex flex-col gap-1">
//                         <span className="text-sm text-slate-600">Transport mode</span>
//                         <select name='transport' className="border rounded px-3 py-2">
//                             {TRANSPORT.map(t => <option key={t}>{t}</option>)}
//                         </select>
//                     </label>
//                     <label className="flex flex-col gap-1">
//                         <span className="text-sm text-slate-600">Eating out frequency</span>
//                         <select name='eat_out' className="border rounded px-3 py-2">
//                             {EAT_OUT.map(e => <option key={e}>{e}</option>)}
//                         </select>
//                     </label>
//                     <label className="flex flex-col gap-1">
//                         <span className="text-sm text-slate-600">Groceries: usual store</span>
//                         <input name='grocery_stores' className="border rounded px-3 py-2" placeholder="PA / IGA / Metro…" />
//                     </label>
//                     <label className='flex flex-col gap-1'>
//                         <span className="text-sm text-slate-600">Grocery budget per week (CAD)</span>
//                         <input name='grocery_budget' type="number" className="border rounded px-3 py-2" placeholder="60" />
//                     </label>
//                 </section>

//                 <button type="submit" className='mt-4 inline-flex items-center rounded-lg bg-indigo-600 text-white px-5 py-2 font-medium hover:bg-indigo-700'>
//                     Generate My Budget Tracker
//                 </button>
//             </form>
//             {error && <p>{error}</p>}
//         </div>
    
//     );
// }
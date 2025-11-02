import { useState} from 'react';

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
const SCHOOLS = ["McGill University",
                 "Concordia University",
                 "Université de Montréal",
                 "UQAM",
                 "HEC Montréal",
                 "École Polytechnique de Montréal"];
const YEARS = ["U0", "U1", "U2", "U3", "U4+"];
const TRANSPORT = ["STM", "Bixi", "Car"];
const EAT_OUT = ["Never", "1-2x/week", "3-5x/week", "Daily"];

export default function Questionnaire() {
    const [isStudent, setIsStudent] = useState("Yes");
    const [housingType, setHousingType] = useState("With parents");

    return (
        <div className="max-w-4xl mx-auto p-6 space-y-6">
            <h1 className="text-3xl font-bold">Metrix — Student Questionnaire</h1>

            {/* Basic */}
            <section className="grid md:grid-cols-2 gap-4">
                <label className="flex flex-col gap-1">
                    <span className="text-sm text-slate-600">Full name</span>
                    <input className="border rounded px-3 py-2" placeholder="First Last" />
                </label>
                <label className="flex flex-col gap-1">
                    <span className="text-sm text-slate-600">Address</span>
                    <input className="border rounded px-3 py-2" placeholder="123 Rue Sherbrooke O" />
                </label>
            </section>

            {/* Student */}
            <section className="grid md:grid-cols-3 gap-4">
                <label className="flex flex-col gap-1">
                    <span className="text-sm text-slate-600">Are you a student?</span>
                    <select className="border rounded px-3 py-2" value={isStudent} onChange={e=>setIsStudent(e.target.value)}>
                        <option>Yes</option><option>No</option>
                    </select>
                </label>
                
                {isStudent === "Yes" && (
                    <>
                        <label className="flex flex-col gap-1">
                            <span className="text-sm text-slate-600">School</span>
                            <select className="border rounded px-3 py-2">
                                {SCHOOLS.map(s => <option key={s}>{s}</option>)}
                            </select>
                        </label>
                        <label className="flex flex-col gap-1">
                            <span className="text-sm text-slate-600">Year of study</span>
                            <select className="border rounded px-3 py-2">
                                {YEARS.map(y => <option key={y}>{y}</option>)}
                            </select>
                        </label>
                        {/* Program dropdown will depend on school; wire it next */}
                        <label className="md:col-span-3 flex flex-col gap-1">
                            <span className="text-sm text-slate-600">Faculty / Program</span>
                            <select className="border rounded px-3 py-2"><option>Select program</option></select>
                        </label>
                    </>
                )}
            </section>

            {/* Housing */}
            <section className="grid md:grid-cols-2 gap-4">
                <label className="flex flex-col gap-1">
                    <span className="text-sm text-slate-600">Neighbourhood</span>
                    <select className="border rounded px-3 py-2">
                        {NEIGHBOURHOODS.map(n => <option key={n}>{n}</option>)}
                    </select>
                </label>
                <label className="flex flex-col gap-1">
                    <span className="text-sm text-slate-600">Housing type</span>
                    <select className="border rounded px-3 py-2" value={housingType} onChange={e=>setHousingType(e.target.value)}>
                        <option>With parents</option>
                        <option>Rental</option>
                        <option>Residence</option>
                    </select>
                </label>

                {["Rental","Residence"].includes(housingType) && (
                    <label className="md:col-span-2 flex flex-col gap-1">
                        <span className="text-sm text-slate-600">Monthly rent (CAD)</span>
                        <input type="number" className="border rounded px-3 py-2" placeholder="900" />
                    </label>
                )}

            </section>

            {/* Transportation & Food */}
            <section className="grid md:grid-cols-2 gap-4">
                <label className="flex flex-col gap-1">
                    <span className="text-sm text-slate-600">Transport mode</span>
                    <select className="border rounded px-3 py-2">
                        {TRANSPORT.map(t => <option key={t}>{t}</option>)}
                    </select>
                </label>
                <label className="flex flex-col gap-1">
                    <span className="text-sm text-slate-600">Eating out frequency</span>
                    <select className="border rounded px-3 py-2">
                        {EAT_OUT.map(e => <option key={e}>{e}</option>)}
                    </select>
                </label>
                <label className="flex flex-col gap-1">
                    <span className="text-sm text-slate-600">Groceries: usual store</span>
                    <input className="border rounded px-3 py-2" placeholder="PA / IGA / Metro…" />
                </label>
                <label className='flex flex-col gap-1'>
                    <span className="text-sm text-slate-600">Grocery budget per week (CAD)</span>
                    <input type="number" className="border rounded px-3 py-2" placeholder="60" />
                </label>
            </section>

            <button className='mt-4 inline-flex items-center rounded-lg bg-indigo-600 text-white px-5 py-2 font-medium hover:bg-indigo-700'>
                Generate My Budget Tracker
            </button>
        </div>
    );
}
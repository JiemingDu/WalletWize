import { useState, useRef, useEffect} from 'react';
//import { APIProvider, useMapsLibrary } from '@vis.gl/react-google-maps';
import { APILoader, PlacePicker } from '@googlemaps/extended-component-library/react';

const apiKey = import.meta.env.VITE_API_KEY as string;

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

export default function Questionaire(){
    if (!apiKey) {
        return (
            <div className="max-w-4xl mx-auto p-6">
                <p className="text-red-500">
                    VITE_API_KEY is not defined. Please check your .env file.
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
    
    const [isStudent, setIsStudent] = useState("Yes");
    const [housingType, setHousingType] = useState("With parents");
    const [error, setError] = useState('');

    const [address, setAddress] = useState('');
    //for google address autocomplete
    
    

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const form = e.currentTarget;
        const selectedSchool = (form.elements.namedItem("school") as HTMLSelectElement)?.value;
        console.log(selectedSchool);
        const selectedYear = (form.elements.namedItem('year') as HTMLSelectElement).value;
        console.log(selectedYear);
        const selectedTransport = (form.elements.namedItem('transport') as HTMLSelectElement).value;
        console.log(selectedTransport)
        const selectedEat_out = (form.elements.namedItem('eat_out') as HTMLSelectElement).value;
        console.log(selectedEat_out);
        console.log(housingType);
        console.log(isStudent);
        const selectedName = (form.elements.namedItem("name") as HTMLInputElement).value;
        console.log(selectedName);
        //const selectedAddress = (form.elements.namedItem("address") as HTMLSelectElement).value;
        //console.log(selectedAddress);
        console.log(address)
        const selectedProgram = (form.elements.namedItem("program") as HTMLSelectElement).value;
        console.log(selectedProgram);
        const selectedNeighbourhood = (form.elements.namedItem("neighbourhood") as HTMLSelectElement)?.value;
        console.log(selectedNeighbourhood);
        const selectedGroceries = (form.elements.namedItem("grocery_stores") as HTMLInputElement)?.value;
        console.log(selectedGroceries);
        const selectedGrocery_budget = (form.elements.namedItem("grocery_budget") as HTMLInputElement)?.value;
        console.log(selectedGrocery_budget);

        setError('')
        try {
            const res = await fetch(
                'http://127.0.0.1:5000/user_info', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name : selectedName,
                    address : address,
                    school : selectedSchool,
                    year : selectedYear,
                    program : selectedProgram,
                    neighbourhood : selectedNeighbourhood,
                    housingType : housingType,
                    transport : selectedTransport,
                    eat_out : selectedEat_out,
                    grocery_stores : selectedGroceries,
                    grocery_budget: selectedGrocery_budget
                })
                }
            )

            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP ${res.status}`)
            }
            // const data = await res.json();
            // console.log('Response from flask', data)

        } catch (err: any) {
            setError(err.message)
        }

    }

    return (
    
        <div className="max-w-4xl mx-auto p-6 space-y-6">
            <form onSubmit={handleSubmit}>
                <h1 className="text-3xl font-bold">Metrix — Student Questionnaire</h1>

                {/* Basic */}
                <section className="grid md:grid-cols-2 gap-4">
                    <label className="flex flex-col gap-1">
                        <span className="text-sm text-slate-600">Full name</span>
                        <input name='name' className="border rounded px-3 py-2" placeholder="First Last" />
                    </label>
                    <label className="flex flex-col gap-1">
                        <span className="text-sm text-slate-600">Address</span>
                        {/* <input ref={addressInputRef} name='address' autoComplete="off" className="border rounded px-3 py-2" placeholder="123 Rue Sherbrooke O" /> */}
                        <PlacePicker
                            placeholder="123 Rue Sherbrooke O"
                            country={["ca"]}
                            className="border rounded px-3 py-2"
                            onInput={(e: any) => setAddress(e.target.value)}
                            // FIX: Make the handler async to await the data
                            onPlaceChange={async (e: any) => {
                                const place = e.detail //e.detail; // This is the Place stub
                                //e.get_place()
                                if (!place) {
                                    return;
                                }

                                await place.fetchFields({
                                    fields: ['formattedAddress', 'name']
                                });

                                setAddress(place.formattedAddress || place.name || '');
                            }}
                        />
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
                                <select name='school' className="border rounded px-3 py-2">
                                    {SCHOOLS.map(s => <option key={s}>{s}</option>)}
                                </select>
                            </label>
                            <label className="flex flex-col gap-1">
                                <span className="text-sm text-slate-600">Year of study</span>
                                <select name='year' className="border rounded px-3 py-2">
                                    {YEARS.map(y => <option key={y}>{y}</option>)}
                                </select>
                            </label>
                            {/* Program dropdown will depend on school; wire it next */}
                            <label className="md:col-span-3 flex flex-col gap-1">
                                <span className="text-sm text-slate-600">Faculty / Program</span>
                                <select name='program' className="border rounded px-3 py-2"><option>Select program</option></select>
                            </label>
                        </>
                    )}
                </section>

                {/* Housing */}
                <section className="grid md:grid-cols-2 gap-4">
                    <label className="flex flex-col gap-1">
                        <span className="text-sm text-slate-600">Neighbourhood</span>
                        <select name='neighbourhood' className="border rounded px-3 py-2">
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
                        <select name='transport' className="border rounded px-3 py-2">
                            {TRANSPORT.map(t => <option key={t}>{t}</option>)}
                        </select>
                    </label>
                    <label className="flex flex-col gap-1">
                        <span className="text-sm text-slate-600">Eating out frequency</span>
                        <select name='eat_out' className="border rounded px-3 py-2">
                            {EAT_OUT.map(e => <option key={e}>{e}</option>)}
                        </select>
                    </label>
                    <label className="flex flex-col gap-1">
                        <span className="text-sm text-slate-600">Groceries: usual store</span>
                        <input name='grocery_stores' className="border rounded px-3 py-2" placeholder="PA / IGA / Metro…" />
                    </label>
                    <label className='flex flex-col gap-1'>
                        <span className="text-sm text-slate-600">Grocery budget per week (CAD)</span>
                        <input name='grocery_budget' type="number" className="border rounded px-3 py-2" placeholder="60" />
                    </label>
                </section>

                <button type="submit" className='mt-4 inline-flex items-center rounded-lg bg-indigo-600 text-white px-5 py-2 font-medium hover:bg-indigo-700'>
                    Generate My Budget Tracker
                </button>
            </form>
            {error && <p>{error}</p>}
        </div>
    
    );
}
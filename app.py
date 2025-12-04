import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import PyPDF2

<!DOCTYPE html>
<html lang="fr" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MTP | Enterprise AI Architect</title>
    
    <!-- 1. Styles & Frameworks -->
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    
    <!-- 2. React Core -->
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>

    <style>
        /* --- THEME OBSIDIAN --- */
        :root {
            --bg-page: #000000;
            --bg-card: #09090b;
            --border: #27272a;
            --text-main: #e4e4e7;
            --text-muted: #a1a1aa;
            --accent: #fff;
        }

        body { 
            font-family: 'Inter', sans-serif; 
            background-color: var(--bg-page); 
            color: var(--text-main); 
            overflow-x: hidden;
        }
        .font-mono { font-family: 'JetBrains Mono', monospace; }

        /* UTILS */
        .glass-nav {
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
        }
        
        .btn-primary {
            background: white; color: black; font-weight: 600;
            transition: all 0.2s;
        }
        .btn-primary:hover { background: #e4e4e7; transform: translateY(-1px); }

        .bg-grid-subtle {
            background-size: 40px 40px;
            background-image: linear-gradient(to right, rgba(255, 255, 255, 0.05) 1px, transparent 1px),
                              linear-gradient(to bottom, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
            mask-image: linear-gradient(to bottom, black 40%, transparent 100%);
        }

        /* APP STYLES */
        .custom-scroll::-webkit-scrollbar { width: 6px; }
        .custom-scroll::-webkit-scrollbar-track { background: transparent; }
        .custom-scroll::-webkit-scrollbar-thumb { background: #3f3f46; border-radius: 3px; }
        .custom-scroll::-webkit-scrollbar-thumb:hover { background: #52525b; }

        @keyframes fade-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .msg-enter { animation: fade-in 0.3s ease-out forwards; }
    </style>
</head>
<body>

    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect, useRef } = React;

        // --- ICONS SVG ---
        const Icons = {
            Logo: ({c}) => <svg className={c} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>,
            Send: ({c}) => <svg className={c} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>,
            Terminal: ({c}) => <svg className={c} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>,
            Sparkles: ({c}) => <svg className={c} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/></svg>,
            Copy: ({c}) => <svg className={c} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>,
            Paperclip: ({c}) => <svg className={c} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>,
            File: ({c}) => <svg className={c} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/></svg>,
            Globe: ({c}) => <svg className={c} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>,
            Bot: ({c}) => <svg className={c} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="16" r="1"/><path d="M8.5 16h.01"/><path d="M15.5 16h.01"/><path d="M9 6l1 5"/><path d="M15 6l-1 5"/><path d="M12 2v4"/></svg>,
            Play: ({c}) => <svg className={c} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>,
            Check: ({c}) => <svg className={c} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>,
            ArrowRight: ({c}) => <svg className={c} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>,
            X: ({c}) => <svg className={c} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        };

        // --- CONFIGURATION MTP ---
        const API_KEY = "AIzaSyBbo2GVp1c9_h1ZqONM5JQFfYs8NJdPbq8"; // Votre clé
        const MODEL_NAME = "gemini-2.5-flash-preview-09-2025";

        // --- COMPOSANT: L'APPLICATION MTP EMBARQUÉE ---
        const MTP_App = () => {
            const [mode, setMode] = useState('architect'); 
            const [archHistory, setArchHistory] = useState([{ role: "model", text: "MTP Architecte v12.0.\n\nJe suis programmé pour concevoir des IAs de haute précision. Décrivez brièvement votre projet (ou envoyez un lien/fichier) pour commencer." }]);
            const [simHistory, setSimHistory] = useState([]);
            const [input, setInput] = useState("");
            const [loading, setLoading] = useState(false);
            const [loadingStatus, setLoadingStatus] = useState("Calcul...");
            const [artifact, setArtifact] = useState(null);
            const [attachment, setAttachment] = useState(null);
            
            const fileInputRef = useRef(null);
            const scrollRef = useRef(null);

            useEffect(() => {
                if(scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
            }, [archHistory, simHistory, loading, mode]);

            // Scraper Web
            const fetchUrlContent = async (url) => {
                try {
                    const response = await fetch(`https://api.allorigins.win/get?url=${encodeURIComponent(url)}`);
                    const data = await response.json();
                    if (!data.contents) return null;
                    const doc = new DOMParser().parseFromString(data.contents, 'text/html');
                    const scripts = doc.querySelectorAll('script, style, footer, nav, header');
                    scripts.forEach(script => script.remove());
                    let text = doc.body.innerText || "";
                    return text.replace(/\s+/g, ' ').trim().substring(0, 15000);
                } catch (error) { return null; }
            };

            // Gestion Fichiers
            const handleFileSelect = (e) => {
                const file = e.target.files[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onloadend = () => {
                    setAttachment({ name: file.name, type: file.type, data: reader.result.split(',')[1] });
                };
                reader.readAsDataURL(file);
            };
            const removeAttachment = () => { setAttachment(null); if(fileInputRef.current) fileInputRef.current.value = ""; };

            // Appel API
            const callGemini = async (systemPrompt, chatHistory, userMsg, fileData, webContent) => {
                try {
                    const historyParts = chatHistory.map(msg => ({ role: msg.role === 'user' ? 'user' : 'model', parts: [{ text: msg.text }] }));
                    const currentMessageParts = [];
                    let fullText = userMsg;
                    if (webContent) fullText += `\n\n[CONTEXTE WEB] :\n${webContent}\n`;
                    currentMessageParts.push({ text: fullText });
                    if (fileData) currentMessageParts.push({ inlineData: { mimeType: fileData.type, data: fileData.data } });

                    const contents = [{ role: "user", parts: [{ text: systemPrompt }] }, ...historyParts, { role: "user", parts: currentMessageParts }];
                    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${MODEL_NAME}:generateContent?key=${API_KEY}`, {
                        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ contents: contents })
                    });
                    const data = await response.json();
                    return data.candidates?.[0]?.content?.parts?.[0]?.text || "Erreur de réponse.";
                } catch (err) { return "Erreur réseau : " + err.message; }
            };

            const handleSend = async (e) => {
                e.preventDefault();
                if ((!input.trim() && !attachment) || loading) return;
                let txt = input; const file = attachment;
                setInput(""); setAttachment(null); if(fileInputRef.current) fileInputRef.current.value = "";
                setLoading(true);

                // URL Detection
                const urlRegex = /(https?:\/\/[^\s]+)/g;
                const urls = txt.match(urlRegex);
                let webData = null;
                if (urls && urls.length > 0) {
                    setLoadingStatus("Lecture Web...");
                    webData = await fetchUrlContent(urls[0]);
                }

                setLoadingStatus("Analyse neuronale...");
                const displayMsg = txt + (file ? `\n📎 [Fichier: ${file.name}]` : "") + (webData ? `\n🌐 [Lien Web Analysé]` : "");

                if (mode === 'architect') {
                    const newHistory = [...archHistory, { role: "user", text: displayMsg }];
                    setArchHistory(newHistory);

                    // SYSTEM PROMPT INQUISITEUR
                    const mtpSystem = `
                    Tu es MTP, Expert Architecte IA.
                    MISSION: Construire un System Prompt parfait.
                    RÈGLES:
                    1. NE GÉNÈRE PAS LE PROMPT TOUT DE SUITE. Interdit.
                    2. Pose UNE SEULE question à la fois pour valider : Rôle, Cible, Ton, Format, Contraintes.
                    3. Si l'utilisateur est vague, insiste.
                    4. Analyse documents et liens si présents.
                    5. QUAND tout est validé, génère le prompt final en commençant par [GENERATE_ARTIFACT].
                    `;

                    const response = await callGemini(mtpSystem, archHistory.slice(1), txt, file, webData);
                    
                    if (response.includes("[GENERATE_ARTIFACT]")) {
                        const parts = response.split("[GENERATE_ARTIFACT]");
                        setArchHistory(prev => [...prev, { role: "model", text: parts[0].trim() || "Analyse terminée." }]);
                        setArtifact(parts[1].trim());
                    } else {
                        setArchHistory(prev => [...prev, { role: "model", text: response }]);
                    }
                } else {
                    const newSimHistory = [...simHistory, { role: "user", text: displayMsg }];
                    setSimHistory(newSimHistory);
                    const response = await callGemini(artifact, simHistory.slice(1), txt, file, webData);
                    setSimHistory(prev => [...prev, { role: "model", text: response }]);
                }
                setLoading(false);
            };

            const startSimulation = () => { setMode('simulation'); setSimHistory([{ role: "model", text: "Simulation initialisée. Je suis prête." }]); };
            const backToArchitect = () => setMode('architect');
            const copyToClipboard = () => {
                const textArea = document.createElement("textarea"); textArea.value = artifact; document.body.appendChild(textArea); textArea.select();
                try { document.execCommand('copy'); alert("Copié !"); } catch (err) {} document.body.removeChild(textArea);
            };

            const isSim = mode === 'simulation';
            const activeHistory = isSim ? simHistory : archHistory;

            return (
                <div className="flex h-[700px] w-full bg-[#09090b] border border-zinc-800 rounded-xl overflow-hidden shadow-2xl">
                    
                    {/* CHAT */}
                    <div className={`flex-1 flex flex-col transition-all duration-500 ${artifact && !isSim ? 'w-1/2 border-r border-zinc-800' : 'w-full'}`}>
                        <div className="h-14 border-b border-zinc-800 flex items-center justify-between px-4 bg-zinc-900/50">
                            <div className="flex items-center gap-2">
                                <div className={`w-2 h-2 rounded-full ${isSim ? 'bg-indigo-500' : 'bg-white'}`}></div>
                                <h2 className="text-xs font-mono text-zinc-400 tracking-wider">{isSim ? "ENVIRONNEMENT DE TEST" : "MTP ARCHITECT"}</h2>
                            </div>
                            {isSim ? 
                                <button onClick={backToArchitect} className="text-xs text-zinc-500 hover:text-white transition-colors border border-zinc-700 px-2 py-1 rounded">Retour</button> :
                                <div className="text-[10px] text-emerald-500 uppercase font-bold">Online</div>
                            }
                        </div>

                        <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scroll" ref={scrollRef}>
                            {activeHistory.map((msg, idx) => (
                                <div key={idx} className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'} msg-enter`}>
                                    <div className={`max-w-[85%] p-3 text-sm leading-relaxed rounded-lg border ${msg.role === 'user' ? `${isSim ? 'bg-indigo-900/20 border-indigo-500/20 text-indigo-100' : 'bg-white text-black border-white'} rounded-tr-none` : 'bg-zinc-900 border-zinc-800 text-zinc-300 rounded-tl-none'}`}>
                                        <p className="whitespace-pre-wrap">{msg.text}</p>
                                    </div>
                                </div>
                            ))}
                            {loading && <div className="flex justify-start animate-pulse"><div className="bg-zinc-900 px-3 py-2 rounded border border-zinc-800 text-xs text-zinc-500">{loadingStatus}</div></div>}
                        </div>

                        <div className="p-4 bg-[#09090b] border-t border-zinc-800">
                            {attachment && (
                                <div className="mb-2 flex items-center gap-2 bg-zinc-800 px-2 py-1 rounded border border-zinc-700 w-fit text-zinc-300 text-xs">
                                    <Icons.File c="w-3 h-3"/><span className="truncate max-w-[150px]">{attachment.name}</span><button onClick={removeAttachment}><Icons.X c="w-3 h-3 hover:text-white"/></button>
                                </div>
                            )}
                            <form onSubmit={handleSend} className="relative flex items-center bg-zinc-900 border border-zinc-800 rounded-lg p-1 gap-2 focus-within:border-zinc-600 transition-colors">
                                <input type="file" ref={fileInputRef} onChange={handleFileSelect} className="hidden" />
                                <button type="button" onClick={() => fileInputRef.current.click()} className="p-2 text-zinc-500 hover:text-white transition-colors rounded hover:bg-zinc-800"><Icons.Paperclip c="w-4 h-4"/></button>
                                <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder={isSim ? "Testez votre IA..." : "Instructions..."} className="flex-1 bg-transparent text-zinc-200 px-2 py-2 focus:outline-none text-sm" autoFocus />
                                <button disabled={(!input.trim() && !attachment) || loading} className={`p-2 ${isSim ? 'bg-indigo-600 hover:bg-indigo-500' : 'bg-white hover:bg-zinc-200'} ${isSim ? 'text-white' : 'text-black'} rounded transition-all disabled:opacity-50`}><Icons.Send c="w-4 h-4"/></button>
                            </form>
                        </div>
                    </div>

                    {/* RESULTAT */}
                    {artifact && !isSim && (
                        <div className="w-[400px] bg-[#0c0c0e] flex flex-col border-l border-zinc-800 animate-slide-in">
                            <div className="h-14 border-b border-zinc-800 flex items-center justify-between px-4 bg-[#0c0c0e]">
                                <div className="flex items-center gap-2 text-zinc-300 text-xs font-medium"><Icons.Sparkles c="w-4 h-4"/> PROMPT GÉNÉRÉ</div>
                                <button onClick={copyToClipboard} className="text-xs text-zinc-500 hover:text-white flex items-center gap-1"><Icons.Copy c="w-3 h-3"/> Copier</button>
                            </div>
                            <div className="flex-1 overflow-y-auto p-4 custom-scroll">
                                <div className="font-mono text-xs text-zinc-400 leading-relaxed whitespace-pre-wrap">{artifact}</div>
                            </div>
                            <div className="p-4 border-t border-zinc-800 bg-[#09090b]">
                                <button onClick={startSimulation} className="w-full py-3 bg-white hover:bg-zinc-200 text-black rounded-lg font-bold text-sm transition-colors flex items-center justify-center gap-2">
                                    <Icons.Play c="w-4 h-4"/> TESTER LA SIMULATION
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            );
        };

        // --- SITE WEB STRUCTURE ---
        const Navbar = () => (
            <nav className="fixed w-full z-50 glass-nav h-16 flex items-center justify-between px-6 lg:px-20 border-b border-[#27272a]">
                <div className="flex items-center gap-2 font-bold text-lg tracking-tight text-white">
                    <div className="w-8 h-8 bg-white rounded flex items-center justify-center text-black"><Icons.Logo c="w-5 h-5"/></div>
                    MTP<span className="text-zinc-500">.PRO</span>
                </div>
                <div className="hidden md:flex items-center gap-8 text-sm font-medium text-zinc-400">
                    <a href="#product" className="hover:text-white transition-colors">Produit</a>
                    <a href="#pricing" className="hover:text-white transition-colors">Tarifs</a>
                    <a href="#demo" className="hover:text-white transition-colors">Essai</a>
                </div>
                <div className="flex items-center gap-4">
                    <a href="#" className="text-sm text-zinc-400 hover:text-white">Connexion</a>
                    <a href="#demo" className="bg-white text-black px-4 py-2 rounded-md text-sm font-semibold hover:bg-zinc-200 transition-colors">Lancer l'App</a>
                </div>
            </nav>
        );

        const Hero = () => (
            <section className="pt-32 pb-20 lg:pt-48 lg:pb-32 px-6 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-full bg-grid-subtle -z-10 opacity-30"></div>
                <div className="max-w-4xl mx-auto text-center">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-zinc-800 bg-zinc-900/50 text-zinc-400 text-xs font-mono mb-8">
                        <span className="w-2 h-2 bg-emerald-500 rounded-full"></span> v12.0 Enterprise Ready
                    </div>
                    <h1 className="text-5xl lg:text-7xl font-extrabold tracking-tight text-white leading-[1.1] mb-6">
                        Industrialisez votre<br/><span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-zinc-500">Intelligence Artificielle.</span>
                    </h1>
                    <p className="text-lg text-zinc-400 mb-10 max-w-xl mx-auto leading-relaxed">
                        MTP génère, teste et déploie des agents IA sur mesure pour vos équipes. Sans code. Sans ingénieur. Avec une précision chirurgicale.
                    </p>
                    <div className="flex justify-center gap-4">
                        <a href="#demo" className="bg-white text-black px-8 py-3 rounded-lg font-semibold hover:bg-zinc-200 transition-all flex items-center gap-2">
                            <Icons.Play c="w-4 h-4" /> Essayer Maintenant
                        </a>
                        <a href="#pricing" className="px-8 py-3 rounded-lg border border-zinc-700 text-zinc-300 hover:text-white hover:bg-zinc-800 transition-all">
                            Voir les Offres
                        </a>
                    </div>
                </div>
            </section>
        );

        const AppDemo = () => (
            <section id="demo" className="py-12 px-6">
                <div className="max-w-6xl mx-auto">
                    <div className="text-center mb-12">
                        <h2 className="text-2xl font-bold text-white mb-2">Console Interactive</h2>
                        <p className="text-zinc-500">Testez la puissance de MTP directement dans votre navigateur.</p>
                    </div>
                    {/* INTEGRATION DE L'APP DANS LE SITE */}
                    <MTP_App />
                </div>
            </section>
        );

        const Pricing = () => (
            <section id="pricing" className="py-24 border-t border-zinc-900 bg-zinc-950">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl font-bold text-white mb-4">Tarification Simple</h2>
                        <p className="text-zinc-500">Des outils professionnels pour des résultats professionnels.</p>
                    </div>
                    <div className="grid md:grid-cols-3 gap-8">
                        {/* Starter */}
                        <div className="p-8 border border-zinc-800 bg-zinc-900/30 rounded-xl">
                            <div className="text-zinc-400 font-medium mb-4">Starter</div>
                            <div className="text-3xl font-bold text-white mb-6">Gratuit</div>
                            <ul className="space-y-3 mb-8 text-sm text-zinc-400">
                                <li className="flex gap-2"><Icons.Check c="w-4 h-4 text-white"/> MTP Architect Basic</li>
                                <li className="flex gap-2"><Icons.Check c="w-4 h-4 text-white"/> 3 Projets / jour</li>
                                <li className="flex gap-2"><Icons.Check c="w-4 h-4 text-white"/> Communauté</li>
                            </ul>
                            <button className="w-full py-2 border border-zinc-700 rounded-lg text-white hover:bg-zinc-800">S'inscrire</button>
                        </div>
                        
                        {/* Pro */}
                        <div className="p-8 border border-white bg-zinc-900 rounded-xl relative transform scale-105 shadow-2xl">
                            <div className="text-white font-medium mb-4">Freelance</div>
                            <div className="text-3xl font-bold text-white mb-1">49€ <span className="text-base font-normal text-zinc-500">/mois</span></div>
                            <div className="text-xs text-zinc-500 mb-6">Facturé annuellement</div>
                            <ul className="space-y-3 mb-8 text-sm text-zinc-300">
                                <li className="flex gap-2"><Icons.Check c="w-4 h-4 text-white"/> <strong>Créations Illimitées</strong></li>
                                <li className="flex gap-2"><Icons.Check c="w-4 h-4 text-white"/> Mode Inquisiteur (Expert)</li>
                                <li className="flex gap-2"><Icons.Check c="w-4 h-4 text-white"/> Analyse de Fichiers & Web</li>
                                <li className="flex gap-2"><Icons.Check c="w-4 h-4 text-white"/> Licence Commerciale</li>
                            </ul>
                            <button className="w-full py-3 bg-white text-black font-bold rounded-lg hover:bg-zinc-200">Commencer</button>
                        </div>

                        {/* Enterprise */}
                        <div className="p-8 border border-zinc-800 bg-zinc-900/30 rounded-xl">
                            <div className="text-zinc-400 font-medium mb-4">Business</div>
                            <div className="text-3xl font-bold text-white mb-1">499€ <span className="text-base font-normal text-zinc-500">/an</span></div>
                            <div className="text-xs text-zinc-500 mb-6">Accès complet pour 5 utilisateurs</div>
                            <ul className="space-y-3 mb-8 text-sm text-zinc-400">
                                <li className="flex gap-2"><Icons.Check c="w-4 h-4 text-white"/> Tout le plan Freelance</li>
                                <li className="flex gap-2"><Icons.Check c="w-4 h-4 text-white"/> <strong>5 Sièges Inclus</strong></li>
                                <li className="flex gap-2"><Icons.Check c="w-4 h-4 text-white"/> Support Prioritaire</li>
                                <li className="flex gap-2"><Icons.Check c="w-4 h-4 text-white"/> API Access</li>
                            </ul>
                            <button className="w-full py-2 border border-zinc-700 rounded-lg text-white hover:bg-zinc-800">Contacter les ventes</button>
                        </div>
                    </div>
                </div>
            </section>
        );

        const Footer = () => (
            <footer className="border-t border-zinc-900 py-12 text-center">
                <p className="text-zinc-600 text-xs">© 2025 MTP Technologies.</p>
            </footer>
        );

        const Website = () => (
            <div className="min-h-screen flex flex-col">
                <Navbar />
                <Hero />
                <AppDemo />
                <Pricing />
                <Footer />
            </div>
        );

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<Website />);
    </script>
</body>
</html>

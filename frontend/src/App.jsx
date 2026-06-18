import React, { useState, useRef } from 'react';
import { 
  Search, BrainCircuit, Database, Network, FileText, 
  Lightbulb, Beaker, AlertTriangle, Loader2, Sparkles, 
  ChevronRight, UploadCloud, CheckCircle2,  Settings, LayoutDashboard
} from 'lucide-react';

export default function App() {
  // Search States
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Upload States
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadComplete, setUploadComplete] = useState(false);
  const fileInputRef = useRef(null);

  // --- Handlers ---
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) throw new Error(`Server Error: ${response.statusText}`);
      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError("Failed to connect to the CogniGraph backend. Ensure your FastAPI server is running.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;
    
    setFile(selectedFile);
    setIsUploading(true);
    setUploadComplete(false);

    // Create a FormData object to send the file
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');
      
      setIsUploading(false);
      setUploadComplete(true);
      
      // Reset success message after 4 seconds
      setTimeout(() => setUploadComplete(false), 4000);
    } catch (err) {
      console.error("Error uploading file:", err);
      setIsUploading(false);
      // Optional: You could set an error state here to show in the UI
      alert("Failed to process document. Check backend logs.");
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-200 font-sans selection:bg-indigo-500/30 flex flex-col relative overflow-hidden">
      
      {/* Ambient Background Glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-indigo-600/10 blur-[120px] pointer-events-none" />
      <div className="absolute top-[20%] right-[-10%] w-[40%] h-[40%] rounded-full bg-blue-600/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] left-[20%] w-[50%] h-[50%] rounded-full bg-purple-600/10 blur-[150px] pointer-events-none" />

      {/* --- PROFESSIONAL NAVBAR --- */}
      <nav className="sticky top-0 z-50 w-full bg-[#0B0F19]/80 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 md:px-8 h-16 flex items-center justify-between">
          
          {/* Logo Identity */}
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-indigo-500 to-blue-600 rounded-lg shadow-[0_0_15px_rgba(99,102,241,0.4)]">
              <Network className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white flex items-center gap-1">
              CogniGraph <span className="text-indigo-400">AI</span>
            </span>
          </div>

          {/* Desktop Nav Links */}
          {/* <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
            <a href="#" className="flex items-center gap-2 hover:text-indigo-400 transition-colors">
              <LayoutDashboard className="w-4 h-4" /> Workspace
            </a>
            <a href="#" className="flex items-center gap-2 text-indigo-400 transition-colors">
              <Database className="w-4 h-4" /> Knowledge Base
            </a>
            <a href="#" className="flex items-center gap-2 hover:text-indigo-400 transition-colors">
              <Settings className="w-4 h-4" /> System Config
            </a>
          </div> */}

          {/* Status Indicator */}
          {/* <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Systems Online</span>
          </div> */}
        </div>
      </nav>

      {/* --- MAIN CONTENT CONTENT --- */}
      <main className="flex-grow relative z-10 p-4 md:p-8 max-w-5xl mx-auto w-full">
        
        {/* Hero Section */}
        <header className="mb-12 mt-8 flex flex-col items-center justify-center text-center animate-in fade-in slide-in-from-top-4 duration-700">
          <div className="inline-flex items-center gap-2 px-3 py-1 mb-6 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-semibold uppercase tracking-widest shadow-[0_0_15px_rgba(99,102,241,0.2)]">
            <Sparkles className="w-3 h-3" />
            <span>Multi-Agent Research Engine</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-gradient-to-br from-white via-slate-200 to-slate-500 bg-clip-text text-transparent mb-4">
            Analyze literature at scale.
          </h1>
          <p className="text-slate-400 text-lg max-w-xl font-light">
            Upload complex academic PDFs. Our agentic workflow orchestrates Qdrant vectors and Neo4j relational logic to synthesize findings instantly.
          </p>
        </header>

        {/* --- UPLOAD SECTION --- */}
        <section className="mb-10 max-w-3xl mx-auto z-20 relative animate-in fade-in duration-700 delay-150">
          <div 
            className={`relative p-6 md:p-8 rounded-3xl border-2 border-dashed transition-all duration-300 flex flex-col items-center justify-center text-center overflow-hidden
              ${isUploading ? 'border-indigo-500 bg-indigo-500/5' : 
                uploadComplete ? 'border-emerald-500 bg-emerald-500/5' : 
                'border-white/10 bg-[#131B2C]/50 hover:bg-[#131B2C]/80 hover:border-indigo-500/50 backdrop-blur-xl'}`}
          >
            <input 
              type="file" 
              accept=".pdf" 
              className="hidden" 
              ref={fileInputRef} 
              onChange={handleFileUpload} 
              disabled={isUploading}
            />
            
            {isUploading ? (
              <div className="flex flex-col items-center">
                <div className="w-16 h-16 relative mb-4">
                  <div className="absolute inset-0 rounded-full border-4 border-indigo-500/20"></div>
                  <div className="absolute inset-0 rounded-full border-4 border-indigo-500 border-t-transparent animate-spin"></div>
                  <UploadCloud className="w-6 h-6 text-indigo-400 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
                </div>
                <h3 className="text-lg font-medium text-slate-200">Ingesting Document...</h3>
                <p className="text-sm text-slate-400 mt-1">Chunking, embedding, and mapping to Graph DB.</p>
              </div>
            ) : uploadComplete ? (
              <div className="flex flex-col items-center text-emerald-400 animate-in zoom-in duration-300">
                <CheckCircle2 className="w-12 h-12 mb-3" />
                <h3 className="text-lg font-medium text-emerald-300">Document Added to Knowledge Base</h3>
                <p className="text-sm text-emerald-500/70 mt-1">{file?.name}</p>
              </div>
            ) : (
              <>
                <div className="w-14 h-14 bg-white/5 rounded-full flex items-center justify-center mb-4 shadow-inner">
                  <UploadCloud className="w-7 h-7 text-indigo-400" />
                </div>
                <h3 className="text-lg font-medium text-slate-200 mb-1">Populate Knowledge Base</h3>
                <p className="text-sm text-slate-400 mb-6 max-w-sm">
                  Drag and drop a research paper (PDF), or click to browse. We'll automatically build the dense vectors and graph relations.
                </p>
                <button 
                  onClick={() => fileInputRef.current?.click()}
                  className="px-6 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded-xl font-medium transition-all shadow-lg text-sm flex items-center gap-2"
                >
                  <FileText className="w-4 h-4" /> Select PDF Document
                </button>
              </>
            )}
          </div>
        </section>

        {/* --- SEARCH BAR SECTION --- */}
        <section className="mb-16 max-w-3xl mx-auto z-20 relative">
          <form onSubmit={handleSearch} className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-blue-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500" />
            
            <div className="relative flex items-center">
              <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-indigo-400/70" />
              </div>
              <input
                type="text"
                className="block w-full pl-14 pr-36 py-5 bg-[#0f172a]/90 backdrop-blur-xl border border-white/10 rounded-2xl text-slate-100 placeholder-slate-500/70 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 shadow-2xl text-lg transition-all"
                placeholder="Ask a complex query against your documents..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !query.trim()}
                className="absolute right-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-500 text-white font-medium rounded-xl transition-all flex items-center gap-2 shadow-[0_0_20px_rgba(79,70,229,0.3)] hover:shadow-[0_0_25px_rgba(79,70,229,0.5)] disabled:shadow-none"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Analyzing</span>
                  </>
                ) : (
                  <>
                    <span>Research</span>
                    <ChevronRight className="w-4 h-4 opacity-70" />
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Error State */}
          {error && (
            <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 backdrop-blur-md rounded-2xl flex items-center gap-3 text-red-400 animate-in fade-in slide-in-from-top-2">
              <AlertTriangle className="w-5 h-5 flex-shrink-0" />
              <p className="font-medium text-sm">{error}</p>
            </div>
          )}
        </section>

        {/* --- RESULTS SECTION --- */}
        {result && result.summary && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700 pb-10">
            
            {/* Metrics Dashboard */}
            {/* <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-[#131B2C]/80 backdrop-blur-xl border border-white/5 rounded-2xl p-6 flex items-center gap-5 shadow-xl hover:border-emerald-500/30 transition-colors group">
                <div className="p-4 bg-emerald-500/10 rounded-xl group-hover:bg-emerald-500/20 transition-colors">
                  <Database className="w-7 h-7 text-emerald-400" />
                </div>
                <div>
                  <p className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-1">Dense Vector Chunks</p>
                  <p className="text-3xl font-bold text-slate-100 flex items-baseline gap-2">
                    {result.vector_sources_count} <span className="text-sm font-normal text-emerald-500/70">retrieved</span>
                  </p>
                </div>
              </div>
              
              <div className="bg-[#131B2C]/80 backdrop-blur-xl border border-white/5 rounded-2xl p-6 flex items-center gap-5 shadow-xl hover:border-purple-500/30 transition-colors group">
                <div className="p-4 bg-purple-500/10 rounded-xl group-hover:bg-purple-500/20 transition-colors">
                  <Network className="w-7 h-7 text-purple-400" />
                </div>
                <div>
                  <p className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-1">Graph Relations</p>
                  <p className="text-3xl font-bold text-slate-100 flex items-baseline gap-2">
                    {result.graph_relations_count} <span className="text-sm font-normal text-purple-500/70">traversed</span>
                  </p>
                </div>
              </div>
            </div> */}

            {/* Structured Summary Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* Methodology */}
              <div className="bg-[#131B2C]/80 backdrop-blur-xl border border-white/5 rounded-3xl p-8 shadow-2xl relative overflow-hidden group hover:border-blue-500/40 hover:-translate-y-1 transition-all duration-300 lg:col-span-2">
                <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/5 rounded-full blur-3xl -mr-20 -mt-20 group-hover:bg-blue-500/10 transition-colors"></div>
                <div className="flex items-center gap-3 mb-6 relative z-10">
                  <div className="p-2 bg-blue-500/10 rounded-lg">
                    <Beaker className="w-5 h-5 text-blue-400" />
                  </div>
                  <h3 className="text-xl font-semibold text-slate-100 tracking-tight">Methodology</h3>
                </div>
                <p className="text-slate-300 leading-relaxed relative z-10 font-light">
                  {result.summary.methodology || "No methodology extracted from the context."}
                </p>
              </div>

              {/* Data Gaps */}
              {/* <div className="bg-[#131B2C]/80 backdrop-blur-xl border border-white/5 rounded-3xl p-8 shadow-2xl relative overflow-hidden group hover:border-amber-500/40 hover:-translate-y-1 transition-all duration-300">
                <div className="absolute top-0 right-0 w-64 h-64 bg-amber-500/5 rounded-full blur-3xl -mr-20 -mt-20 group-hover:bg-amber-500/10 transition-colors"></div>
                <div className="flex items-center gap-3 mb-6 relative z-10">
                  <div className="p-2 bg-amber-500/10 rounded-lg">
                    <AlertTriangle className="w-5 h-5 text-amber-400" />
                  </div>
                  <h3 className="text-xl font-semibold text-slate-100 tracking-tight">Limitations & Gaps</h3>
                </div>
                <p className="text-slate-300 leading-relaxed relative z-10 font-light">
                  {result.summary.data_gaps || "No specific limitations noted by the authors."}
                </p>
              </div> */}

              {/* Key Findings (Spans full width) */}
              <div className="bg-[#131B2C]/80 backdrop-blur-xl border border-white/5 rounded-3xl p-8 shadow-2xl lg:col-span-2 relative overflow-hidden group hover:border-emerald-500/40 transition-all duration-300">
                <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl -mr-20 -mt-20 group-hover:bg-emerald-500/10 transition-colors"></div>
                <div className="flex items-center gap-3 mb-8 relative z-10">
                  <div className="p-2 bg-emerald-500/10 rounded-lg">
                    <Lightbulb className="w-5 h-5 text-emerald-400" />
                  </div>
                  <h3 className="text-xl font-semibold text-slate-100 tracking-tight">Key Findings & Hypotheses</h3>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-10 relative z-10">
                  <div>
                    <h4 className="text-xs font-semibold text-emerald-400 mb-4 uppercase tracking-widest flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]"></span>
                      Core Hypotheses
                    </h4>
                    <ul className="space-y-4">
                      {result.summary.core_hypotheses?.length > 0 ? (
                        result.summary.core_hypotheses.map((hypothesis, idx) => (
                          <li key={idx} className="text-slate-300 text-sm flex items-start gap-3 bg-white/5 p-3 rounded-xl border border-white/5">
                            <span className="text-emerald-500 font-bold mt-0.5">•</span>
                            <span className="leading-relaxed">{hypothesis}</span>
                          </li>
                        ))
                      ) : (
                        <li className="text-slate-500 text-sm italic">None extracted.</li>
                      )}
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="text-xs font-semibold text-blue-400 mb-4 uppercase tracking-widest flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-blue-400 shadow-[0_0_8px_rgba(96,165,250,0.8)]"></span>
                      Measurable Results
                    </h4>
                    <ul className="space-y-4">
                      {result.summary.key_findings?.length > 0 ? (
                        result.summary.key_findings.map((finding, idx) => (
                          <li key={idx} className="text-slate-300 text-sm flex items-start gap-3 bg-white/5 p-3 rounded-xl border border-white/5">
                            <span className="text-blue-500 mt-0.5 font-bold">→</span>
                            <span className="leading-relaxed">{finding}</span>
                          </li>
                        ))
                      ) : (
                        <li className="text-slate-500 text-sm italic">None extracted.</li>
                      )}
                    </ul>
                  </div>
                </div>
              </div>

            </div>
          </div>
        )}
      </main>

      {/* --- PROFESSIONAL FOOTER --- */}
      <footer className="border-t border-white/5 bg-[#080B13] py-8 mt-auto relative z-10">
        <div className="max-w-7xl mx-auto px-4 md:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Network className="w-4 h-4 text-indigo-400" />
            <span className="text-slate-400 text-sm font-medium">CogniGraph AI © {new Date().getFullYear()}</span>
          </div>
          
          <div className="flex items-center gap-6">
            {/* <a href="#" className="text-slate-500 hover:text-white transition-colors flex items-center gap-2 text-sm">
              <Github className="w-4 h-4" /> Source Code
            </a> */}
            {/* <a href="#" className="text-slate-500 hover:text-white transition-colors flex items-center gap-2 text-sm">
              <Linkedin className="w-4 h-4" /> Developer Profile
            </a> */}
          </div>
        </div>
      </footer>

    </div>
  );
}
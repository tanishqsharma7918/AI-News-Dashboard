"use client";
import { useEffect, useState } from "react";
import { Star, Share2, RefreshCw, Link as LinkIcon, Newspaper, Flame, Sparkles } from "lucide-react";

// --- INTERFACES ---
interface NewsItem {
  id: number;
  title: string;
  summary: string;
  url: string;
  source_id: number;
  source_name: string;
  published_at: string;
  is_favorite: boolean;
}

interface Topic {
  id: number;
  title: string;
  summary: string;
  popularity_score: number;
  url: string;
}

export default function Dashboard() {
  // --- STATE ---
  const [news, setNews] = useState<NewsItem[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("all");

  // Track open menus for News items AND Topics
  const [openMenuId, setOpenMenuId] = useState<number | null>(null);
  const [openTopicMenuId, setOpenTopicMenuId] = useState<number | null>(null);

  // --- HELPERS ---
  const stripHtml = (html: string) => {
    if (!html) return "";
    return html.replace(/<[^>]*>?/gm, '');
  };

  // --- API CALLS ---
  const fetchNews = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/news");
      const data = await res.json();
      setNews(data);
    } catch (error) {
      console.error("Failed to fetch news:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTopics = async () => {
    try {
      const res = await fetch("http://localhost:8000/topics");
      const data = await res.json();
      setTopics(data);
    } catch (error) {
      console.error("Failed to fetch topics:", error);
    }
  };

  const toggleFavorite = async (id: number) => {
    setNews(news.map(item =>
      item.id === id ? { ...item, is_favorite: !item.is_favorite } : item
    ));
    await fetch(`http://localhost:8000/news/${id}/favorite`, { method: "POST" });
  };

  // Generic Broadcast Handler (Works for News AND Topics)
  const handleBroadcast = async (id: number, platform: string, type: "news" | "topic") => {
    setOpenMenuId(null);
    setOpenTopicMenuId(null);
    try {
      // In a real app, we would have a separate /broadcast-topic endpoint
      // For MVP, we reuse the existing endpoint or simulate it
      const res = await fetch("http://localhost:8000/broadcast", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ news_id: id, platform: platform })
      });
      const data = await res.json();
      if (res.ok) alert(`✅ ${type === "topic" ? "Topic" : "Article"} broadcasted to ${data.platform}`);
    } catch (err) {
      alert("❌ Failed to broadcast");
    }
  };

  const handleCopyLink = (url: string) => {
    navigator.clipboard.writeText(url);
    alert("🔗 Link copied!");
  };

  // --- INITIAL LOAD ---
  useEffect(() => {
    fetchNews();
    fetchTopics();
  }, []);

  const displayedNews = activeTab === "favorites"
    ? news.filter(item => item.is_favorite)
    : news;

  // Handle global click to close menus
  const handleGlobalClick = () => {
    setOpenMenuId(null);
    setOpenTopicMenuId(null);
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans pb-20" onClick={handleGlobalClick}>

      {/* HEADER */}
      <header className="sticky top-0 z-50 bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-blue-600 p-1.5 rounded-lg">
              <Newspaper className="text-white" size={20} />
            </div>
            <h1 className="text-lg font-bold text-slate-900 tracking-tight">AI Pulse Dashboard</h1>
          </div>

          <button
            onClick={() => { fetchNews(); fetchTopics(); }}
            className="p-2 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-all"
            title="Refresh Data"
          >
            <RefreshCw size={20} />
          </button>
        </div>
      </header>

      {/* TABS */}
      <div className="max-w-6xl mx-auto px-6 mt-8 mb-8">
        <div className="inline-flex bg-white p-1 rounded-lg border border-slate-200 shadow-sm">
          <button
            onClick={() => setActiveTab("all")}
            className={`px-5 py-2 rounded-md text-sm font-semibold transition-all ${
              activeTab === "all" ? "bg-slate-900 text-white shadow" : "text-slate-600 hover:bg-slate-50"
            }`}
          >
            All News
          </button>
          <button
            onClick={() => setActiveTab("popular")}
            className={`px-5 py-2 rounded-md text-sm font-semibold transition-all flex items-center ${
              activeTab === "popular" ? "bg-orange-500 text-white shadow" : "text-slate-600 hover:bg-orange-50 hover:text-orange-600"
            }`}
          >
            <Flame size={16} className="mr-1.5" /> Popular
          </button>
          <button
            onClick={() => setActiveTab("favorites")}
            className={`px-5 py-2 rounded-md text-sm font-semibold transition-all ${
              activeTab === "favorites" ? "bg-slate-900 text-white shadow" : "text-slate-600 hover:bg-slate-50"
            }`}
          >
            Favorites ({news.filter(n => n.is_favorite).length})
          </button>
        </div>
      </div>

      {/* CONTENT AREA */}
      <main className="max-w-6xl mx-auto px-6">
        {loading ? (
          <div className="text-center py-20 text-slate-500">Loading Intelligence...</div>
        ) : (
          <>
            {/* VIEW 1: POPULAR TOPICS */}
            {activeTab === "popular" && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {topics.length === 0 && (
                   <div className="col-span-full text-center py-12 text-slate-400">No trending topic clusters found yet.</div>
                )}
                {topics.map((topic) => (
                  <div key={topic.id} className="bg-white p-6 rounded-xl border border-orange-100 shadow-sm hover:shadow-md transition-all relative overflow-visible">
                    <div className="absolute top-0 right-0 p-3 opacity-10 pointer-events-none">
                        <Flame size={100} className="text-orange-500" />
                    </div>

                    {/* Score Badge */}
                    <div className="flex justify-between items-start mb-3 relative z-10">
                      <span className="bg-orange-50 text-orange-700 px-3 py-1 rounded-full text-xs font-bold flex items-center border border-orange-100">
                         <Sparkles size={12} className="mr-1" /> Score: {topic.popularity_score}
                      </span>
                    </div>

                    {/* Clean Title */}
                    <h2 className="text-xl font-bold text-slate-900 relative z-10 leading-tight hover:text-blue-600 transition-colors">
  <a href={topic.url} target="_blank" rel="noreferrer">
    {topic.title}
  </a>
</h2>

                    {/* Cleaned Summary (No HTML) */}
                    <p className="text-slate-600 mt-3 line-clamp-3 text-sm relative z-10">
                        {stripHtml(topic.summary) || "AI-generated summary of this topic cluster..."}
                    </p>

                    {/* Interactive Action Bar */}
                    <div className="mt-5 pt-4 border-t border-slate-100 flex space-x-4 relative z-10">
                       <button
                         onClick={(e) => { e.stopPropagation(); alert(`Opening Cluster View for: ${topic.title}`); }}
                         className="text-sm font-semibold text-blue-600 hover:text-blue-800 hover:underline transition-colors"
                       >
                         View Cluster
                       </button>

                       <div className="relative">
                         <button
                           onClick={(e) => { e.stopPropagation(); setOpenTopicMenuId(openTopicMenuId === topic.id ? null : topic.id); }}
                           className="text-sm font-semibold text-slate-500 hover:text-slate-800 transition-colors flex items-center"
                         >
                           Share Topic <Share2 size={12} className="ml-1" />
                         </button>

                         {/* Topic Share Menu */}
                         {openTopicMenuId === topic.id && (
                            <div className="absolute top-full left-0 mt-2 w-36 bg-white border border-slate-200 rounded-lg shadow-xl z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-150" onClick={(e) => e.stopPropagation()}>
                              {["LinkedIn", "WhatsApp", "Email"].map((platform) => (
                                <button
                                  key={platform}
                                  onClick={() => handleBroadcast(topic.id, platform, "topic")}
                                  className="w-full text-left px-4 py-2 hover:bg-slate-50 text-slate-700 text-xs font-medium"
                                >
                                  {platform}
                                </button>
                              ))}
                            </div>
                          )}
                       </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* VIEW 2: STANDARD NEWS GRID */}
            {activeTab !== "popular" && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {displayedNews.length === 0 && (
                  <div className="col-span-full text-center py-12 bg-white rounded-xl border border-slate-200 border-dashed">
                    <p className="text-slate-400">No stories found.</p>
                  </div>
                )}

                {displayedNews.map((item) => (
                  <div key={item.id} className="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-lg hover:border-blue-200 transition-all duration-300 flex flex-col h-full overflow-hidden">
                    <div className="p-5 flex flex-col h-full">
                      <div className="flex justify-between items-center mb-3">
                        <span className="text-[11px] font-bold text-blue-600 uppercase tracking-wider truncate max-w-[70%]">
                          {item.source_name}
                        </span>
                        <span className="text-xs text-slate-400">
                          {new Date(item.published_at).toLocaleDateString()}
                        </span>
                      </div>

                      <div className="flex-grow">
                        <h2 className="text-base font-bold text-slate-900 leading-snug mb-2 hover:text-blue-600">
                          <a href={item.url} target="_blank" rel="noreferrer">
                            {item.title}
                          </a>
                        </h2>
                        <p className="text-sm text-slate-500 leading-relaxed line-clamp-3">
                          {stripHtml(item.summary)}
                        </p>
                      </div>

                      <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between">
                        <div className="flex space-x-1">
                          <button
                            onClick={(e) => { e.stopPropagation(); toggleFavorite(item.id); }}
                            className={`p-2 rounded-md transition-colors ${
                              item.is_favorite ? "text-yellow-500 bg-yellow-50" : "text-slate-400 hover:bg-slate-50 hover:text-slate-600"
                            }`}
                          >
                            <Star size={18} fill={item.is_favorite ? "currentColor" : "none"} />
                          </button>
                          <button
                            onClick={(e) => { e.stopPropagation(); handleCopyLink(item.url); }}
                            className="p-2 rounded-md text-slate-400 hover:bg-slate-50 hover:text-blue-600 transition-colors"
                          >
                            <LinkIcon size={18} />
                          </button>
                        </div>

                        {item.is_favorite && (
                          <div className="relative">
                            <button
                              onClick={(e) => { e.stopPropagation(); setOpenMenuId(openMenuId === item.id ? null : item.id); }}
                              className={`flex items-center space-x-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                                openMenuId === item.id ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                              }`}
                            >
                              <span>Share</span>
                              <Share2 size={14} />
                            </button>

                            {openMenuId === item.id && (
                              <div className="absolute bottom-full right-0 mb-2 w-32 bg-white border border-slate-200 rounded-lg shadow-xl z-50 overflow-hidden" onClick={(e) => e.stopPropagation()}>
                                {["LinkedIn", "WhatsApp", "Email"].map((platform) => (
                                  <button
                                    key={platform}
                                    onClick={() => handleBroadcast(item.id, platform, "news")}
                                    className="w-full text-left px-4 py-2 hover:bg-slate-50 text-slate-700 text-xs font-medium"
                                  >
                                    {platform}
                                  </button>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
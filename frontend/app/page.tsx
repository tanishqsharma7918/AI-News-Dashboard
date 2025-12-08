"use client";
import { useEffect, useState } from "react";
import {
  Star,
  Share2,
  RefreshCw,
  Link as LinkIcon,
  Newspaper,
  Flame,
  Sparkles,
  X,
  ExternalLink,
  TrendingUp,
  Clock,
} from "lucide-react";

// --- ENV BASE URL ---
const API_BASE = process.env.NEXT_PUBLIC_API_URL;

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

interface TopicArticle {
  id: number;
  title: string;
  url: string;
  source_id: number;
  published_at: string;
}

interface Topic {
  id: number;
  title: string;
  summary: string;
  popularity_score: number;
  url: string;
  articles: TopicArticle[];
}

export default function Dashboard() {
  // --- STATE ---
  const [news, setNews] = useState<NewsItem[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("all");
  const [openMenuId, setOpenMenuId] = useState<number | null>(null);
  const [openTopicMenuId, setOpenTopicMenuId] = useState<number | null>(null);
  const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);

  // --- HELPERS ---
  const stripHtml = (html: string) => {
    if (!html) return "";
    return html.replace(/<[^>]*>?/gm, "");
  };

  // --- SHARE HELPERS ---
  const shareToPlatform = (platform: string, title: string, url: string) => {
    const encodedTitle = encodeURIComponent(title);
    const encodedUrl = encodeURIComponent(url);
    let shareUrl = "";

    if (platform === "LinkedIn") {
      shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`;
    }

    if (platform === "WhatsApp") {
      shareUrl = `https://wa.me/?text=${encodedTitle}%20-%20${encodedUrl}`;
    }

    if (platform === "Email") {
      shareUrl = `mailto:?subject=${encodedTitle}&body=${encodedTitle}%0A${encodedUrl}`;
    }

    window.open(shareUrl, "_blank");
  };

  const handleBroadcast = (
    id: number,
    platform: string,
    type: "news" | "topic"
  ) => {
    setOpenMenuId(null);
    setOpenTopicMenuId(null);

    const item =
      type === "news"
        ? news.find((n) => n.id === id)
        : topics.find((t) => t.id === id);

    if (!item) return;

    shareToPlatform(platform, item.title, item.url);
  };

  const handleCopyLink = (url: string) => {
    navigator.clipboard.writeText(url);
    alert("🔗 Link copied!");
  };

  // --- API CALLS ---
  const fetchNews = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/news`);
      setNews(await res.json());
    } catch (err) {
      console.error("Error fetching news:", err);
    }
    setLoading(false);
  };

  const fetchTopics = async () => {
    try {
      const res = await fetch(`${API_BASE}/topics`);
      setTopics(await res.json());
    } catch (err) {
      console.error("Error fetching topics:", err);
    }
  };

  const toggleFavorite = async (id: number) => {
    setNews(
      news.map((item) =>
        item.id === id ? { ...item, is_favorite: !item.is_favorite } : item
      )
    );

    try {
      await fetch(`${API_BASE}/news/${id}/favorite`, {
        method: "POST",
      });
    } catch (err) {
      console.error("Error toggling favorite:", err);
    }
  };

  useEffect(() => {
    fetchNews();
    fetchTopics();
  }, []);

  const displayedNews =
    activeTab === "favorites"
      ? news.filter((item) => item.is_favorite)
      : news;

  const handleGlobalClick = () => {
    setOpenMenuId(null);
    setOpenTopicMenuId(null);
  };

  return (
    <div
      className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-purple-50/20 font-sans pb-20"
      onClick={handleGlobalClick}
    >
      {/* HEADER */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-slate-200/60 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl blur opacity-75"></div>
              <div className="relative bg-gradient-to-br from-blue-600 to-indigo-600 p-2.5 rounded-2xl">
                <Newspaper className="text-white" size={24} />
              </div>
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-900 via-blue-800 to-indigo-900 bg-clip-text text-transparent">
                AI Pulse
              </h1>
              <p className="text-xs text-slate-500 font-medium">Intelligence Dashboard</p>
            </div>
          </div>

          <button
            onClick={() => {
              fetchNews();
              fetchTopics();
            }}
            className="group relative p-3 text-slate-600 hover:text-blue-600 bg-slate-100 hover:bg-blue-50 rounded-xl transition-all duration-300 hover:scale-105"
          >
            <RefreshCw size={20} className="group-hover:rotate-180 transition-transform duration-500" />
          </button>
        </div>
      </header>

      {/* TABS */}
      <div className="max-w-7xl mx-auto px-6 mt-10 mb-10">
        <div className="inline-flex bg-white/60 backdrop-blur-xl p-1.5 rounded-2xl border border-slate-200/60 shadow-lg">
          <button
            onClick={() => setActiveTab("all")}
            className={`px-6 py-3 rounded-xl text-sm font-bold transition-all duration-300 ${
              activeTab === "all"
                ? "bg-gradient-to-r from-slate-900 to-slate-700 text-white shadow-lg shadow-slate-900/30 scale-105"
                : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
            }`}
          >
            All News
          </button>
          <button
            onClick={() => setActiveTab("popular")}
            className={`px-6 py-3 rounded-xl text-sm font-bold transition-all duration-300 flex items-center ${
              activeTab === "popular"
                ? "bg-gradient-to-r from-orange-500 to-red-500 text-white shadow-lg shadow-orange-500/30 scale-105"
                : "text-slate-600 hover:bg-orange-50 hover:text-orange-600"
            }`}
          >
            <Flame size={16} className="mr-2" /> Popular
          </button>
          <button
            onClick={() => setActiveTab("favorites")}
            className={`px-6 py-3 rounded-xl text-sm font-bold transition-all duration-300 ${
              activeTab === "favorites"
                ? "bg-gradient-to-r from-yellow-500 to-amber-500 text-white shadow-lg shadow-yellow-500/30 scale-105"
                : "text-slate-600 hover:bg-yellow-50 hover:text-yellow-600"
            }`}
          >
            <Star size={16} className="inline mr-2" />
            Favorites ({news.filter((n) => n.is_favorite).length})
          </button>
        </div>
      </div>

      {/* CONTENT */}
      <main className="max-w-7xl mx-auto px-6">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-32">
            <div className="relative">
              <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
            </div>
            <p className="mt-6 text-slate-600 font-medium">Loading Intelligence...</p>
          </div>
        ) : (
          <>
            {/* POPULAR TOPICS */}
            {activeTab === "popular" && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {topics.map((topic, index) => (
                  <div
                    key={topic.id}
                    className="group relative bg-white/60 backdrop-blur-xl p-8 rounded-3xl border border-orange-100/60 shadow-lg hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 overflow-hidden"
                    style={{
                      animationDelay: `${index * 100}ms`,
                      animation: "fadeInUp 0.6s ease-out forwards",
                    }}
                  >
                    {/* Gradient Background Accent */}
                    <div className="absolute inset-0 bg-gradient-to-br from-orange-50/50 via-transparent to-purple-50/30 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                    
                    {/* Decorative Element */}
                    <div className="absolute -top-6 -right-6 w-32 h-32 bg-gradient-to-br from-orange-400/10 to-red-400/10 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-700"></div>

                    <div className="relative z-10">
                      <div className="flex items-center justify-between mb-4">
                        <span className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-4 py-1.5 rounded-full text-xs font-bold flex items-center shadow-lg shadow-orange-500/20">
                          <Sparkles size={14} className="mr-1.5" />
                          Score: {topic.popularity_score}
                        </span>
                        <div className="flex items-center space-x-2 text-orange-600">
                          <TrendingUp size={16} />
                          <span className="text-xs font-semibold">{topic.articles?.length || 0} sources</span>
                        </div>
                      </div>

                      <h2 className="text-2xl font-bold text-slate-900 mt-4 mb-3 leading-tight group-hover:text-blue-600 transition-colors duration-300">
                        <a href={topic.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                          {topic.title}
                        </a>
                      </h2>

                      <p className="text-slate-600 line-clamp-3 text-sm leading-relaxed">
                        {stripHtml(topic.summary)}
                      </p>

                      <div className="mt-6 pt-5 border-t border-slate-200/60 flex items-center justify-between">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedTopic(topic);
                          }}
                          className="group/btn flex items-center space-x-2 px-4 py-2 bg-blue-50 hover:bg-blue-600 text-blue-600 hover:text-white rounded-xl font-semibold text-sm transition-all duration-300 hover:shadow-lg hover:shadow-blue-600/20"
                        >
                          <span>View Cluster</span>
                          <span className="bg-blue-600 group-hover/btn:bg-white text-white group-hover/btn:text-blue-600 px-2 py-0.5 rounded-full text-xs font-bold transition-colors duration-300">
                            {topic.articles?.length || 0}
                          </span>
                        </button>

                        <div className="relative">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setOpenTopicMenuId(
                                openTopicMenuId === topic.id ? null : topic.id
                              );
                            }}
                            className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-all duration-200"
                          >
                            <Share2 size={18} />
                          </button>

                          {openTopicMenuId === topic.id && (
                            <div className="absolute top-full right-0 mt-2 w-40 bg-white/95 backdrop-blur-xl border border-slate-200 rounded-xl shadow-2xl z-50 overflow-hidden">
                              {["LinkedIn", "WhatsApp", "Email"].map((platform) => (
                                <button
                                  key={platform}
                                  onClick={() =>
                                    handleBroadcast(topic.id, platform, "topic")
                                  }
                                  className="w-full text-left px-4 py-3 hover:bg-slate-50 text-slate-700 text-sm font-medium transition-colors"
                                >
                                  {platform}
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* NEWS GRID */}
            {activeTab !== "popular" && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {displayedNews.map((item, index) => (
                  <div
                    key={item.id}
                    className="group relative bg-white/60 backdrop-blur-xl rounded-2xl border border-slate-200/60 shadow-md hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 overflow-hidden"
                    style={{
                      animationDelay: `${index * 50}ms`,
                      animation: "fadeInUp 0.5s ease-out forwards",
                    }}
                  >
                    {/* Gradient Overlay on Hover */}
                    <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 via-transparent to-purple-50/30 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

                    <div className="relative z-10 p-6">
                      <div className="flex justify-between items-center mb-3">
                        <span className="text-[10px] font-bold text-blue-600 uppercase tracking-wider truncate max-w-[70%] px-2 py-1 bg-blue-50 rounded-md">
                          {item.source_name}
                        </span>
                        <div className="flex items-center space-x-1 text-xs text-slate-400">
                          <Clock size={12} />
                          <span>{new Date(item.published_at).toLocaleDateString()}</span>
                        </div>
                      </div>

                      <h2 className="text-lg font-bold text-slate-900 mb-3 leading-tight group-hover:text-blue-600 transition-colors duration-300 line-clamp-2">
                        <a href={item.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                          {item.title}
                        </a>
                      </h2>

                      <p className="text-sm text-slate-600 line-clamp-3 leading-relaxed">
                        {stripHtml(item.summary)}
                      </p>

                      <div className="mt-5 pt-4 border-t border-slate-200/60 flex items-center justify-between">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => toggleFavorite(item.id)}
                            className={`p-2.5 rounded-xl transition-all duration-300 ${
                              item.is_favorite
                                ? "text-yellow-600 bg-yellow-50 shadow-md shadow-yellow-500/20 scale-110"
                                : "text-slate-400 hover:bg-slate-100 hover:text-yellow-500"
                            }`}
                          >
                            <Star
                              size={18}
                              fill={item.is_favorite ? "currentColor" : "none"}
                              className="transition-all duration-300"
                            />
                          </button>

                          <button
                            onClick={() => handleCopyLink(item.url)}
                            className="p-2.5 rounded-xl text-slate-400 hover:bg-blue-50 hover:text-blue-600 transition-all duration-300"
                          >
                            <LinkIcon size={18} />
                          </button>
                        </div>

                        {item.is_favorite && (
                          <div className="relative">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setOpenMenuId(
                                  openMenuId === item.id ? null : item.id
                                );
                              }}
                              className={`flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all duration-300 ${
                                openMenuId === item.id
                                  ? "bg-slate-900 text-white shadow-lg"
                                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                              }`}
                            >
                              <span>Share</span>
                              <Share2 size={14} />
                            </button>

                            {openMenuId === item.id && (
                              <div className="absolute bottom-full right-0 mb-2 w-36 bg-white/95 backdrop-blur-xl border border-slate-200 rounded-xl shadow-2xl z-50 overflow-hidden">
                                {["LinkedIn", "WhatsApp", "Email"].map((platform) => (
                                  <button
                                    key={platform}
                                    onClick={() =>
                                      handleBroadcast(item.id, platform, "news")
                                    }
                                    className="w-full text-left px-4 py-3 hover:bg-slate-50 text-slate-700 text-xs font-medium transition-colors"
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

      {/* TOPIC CLUSTER MODAL */}
      {selectedTopic && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md animate-fadeIn"
          onClick={() => setSelectedTopic(null)}
        >
          <div
            className="bg-white/95 backdrop-blur-2xl rounded-3xl shadow-2xl w-full max-w-3xl max-h-[85vh] flex flex-col overflow-hidden animate-scaleIn"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="relative p-8 border-b border-slate-200/60 bg-gradient-to-r from-orange-50/50 to-purple-50/30">
              <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-orange-300/10 to-purple-300/10 rounded-full blur-3xl"></div>
              
              <div className="relative">
                <span className="inline-flex items-center text-xs font-bold text-orange-600 uppercase tracking-wider bg-orange-100 px-3 py-1 rounded-full mb-3">
                  <Sparkles size={12} className="mr-1" />
                  Topic Cluster
                </span>
                <h3 className="text-3xl font-bold text-slate-900 leading-tight pr-12">
                  {selectedTopic.title}
                </h3>
              </div>

              <button
                onClick={() => setSelectedTopic(null)}
                className="absolute top-6 right-6 p-2.5 bg-white hover:bg-slate-100 rounded-full text-slate-600 hover:text-slate-900 shadow-lg transition-all duration-300 hover:rotate-90"
              >
                <X size={20} />
              </button>
            </div>

            <div className="overflow-y-auto p-8 space-y-5">
              {selectedTopic.articles.length > 0 ? (
                selectedTopic.articles.map((article, index) => (
                  <div
                    key={article.id}
                    className="group flex items-start p-4 rounded-2xl hover:bg-slate-50 transition-all duration-300"
                    style={{
                      animationDelay: `${index * 80}ms`,
                      animation: "fadeInUp 0.5s ease-out forwards",
                    }}
                  >
                    <div className="mr-4 mt-2">
                      <div className="w-2.5 h-2.5 rounded-full bg-gradient-to-r from-blue-400 to-indigo-500 shadow-md shadow-blue-400/50 group-hover:scale-125 transition-transform duration-300"></div>
                    </div>

                    <div className="flex-1">
                      <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-lg font-bold text-slate-800 hover:text-blue-600 transition-colors duration-300 block mb-2 group-hover:underline"
                      >
                        {article.title}
                      </a>

                      <div className="flex items-center flex-wrap gap-3 text-xs text-slate-500">
                        <span className="bg-slate-100 px-2 py-1 rounded-md font-medium">
                          Source #{article.source_id}
                        </span>
                        <span className="flex items-center space-x-1">
                          <Clock size={12} />
                          <span>{new Date(article.published_at).toLocaleDateString()}</span>
                        </span>
                        <a
                          href={article.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center space-x-1 text-blue-600 hover:text-blue-700 font-medium"
                        >
                          <span>Read</span>
                          <ExternalLink size={12} />
                        </a>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-12">
                  <p className="text-slate-500 italic">
                    No additional articles found in this cluster.
                  </p>
                </div>
              )}
            </div>

            <div className="p-6 border-t border-slate-200/60 bg-slate-50/50 text-center">
              <button
                onClick={() => setSelectedTopic(null)}
                className="px-6 py-3 bg-slate-900 hover:bg-slate-800 text-white font-semibold rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-slate-900/20"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx global>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes scaleIn {
          from {
            opacity: 0;
            transform: scale(0.9);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }

        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }

        .animate-scaleIn {
          animation: scaleIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}

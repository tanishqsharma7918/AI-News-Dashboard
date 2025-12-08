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
  Layers,
  Zap,
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
      className="min-h-screen relative overflow-hidden"
      onClick={handleGlobalClick}
    >
      {/* VisionOS Background */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-indigo-50/30 to-purple-50/20"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(120,119,198,0.1),transparent_50%)]"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,rgba(59,130,246,0.08),transparent_50%)]"></div>
        <div className="absolute inset-0 backdrop-blur-3xl bg-white/40"></div>
      </div>

      {/* HEADER */}
      <header className="sticky top-0 z-50">
        <div className="absolute inset-0 backdrop-blur-2xl bg-white/30 border-b border-white/20 shadow-lg shadow-black/5"></div>
        <div className="relative max-w-7xl mx-auto px-8 h-24 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-400/20 to-indigo-500/20 rounded-[20px] blur-xl group-hover:blur-2xl transition-all duration-500"></div>
              <div className="relative backdrop-blur-xl bg-white/40 p-3 rounded-[20px] border border-white/30 shadow-xl shadow-blue-500/10">
                <Layers className="text-blue-600" size={28} strokeWidth={1.5} />
              </div>
            </div>
            <div>
              <h1 className="text-3xl font-semibold text-slate-800 tracking-tight">
                AI Pulse
              </h1>
              <p className="text-xs text-slate-500 font-medium tracking-wide">Intelligence Dashboard</p>
            </div>
          </div>

          <button
            onClick={() => {
              fetchNews();
              fetchTopics();
            }}
            className="group relative backdrop-blur-xl bg-white/40 p-3.5 rounded-[18px] border border-white/30 shadow-lg shadow-black/5 hover:shadow-xl hover:shadow-blue-500/10 transition-all duration-300 hover:scale-105"
          >
            <RefreshCw 
              size={20} 
              className="text-slate-600 group-hover:text-blue-600 group-hover:rotate-180 transition-all duration-500" 
              strokeWidth={1.5}
            />
          </button>
        </div>
      </header>

      {/* TABS */}
      <div className="max-w-7xl mx-auto px-8 mt-12 mb-12 flex justify-center">
        <div className="inline-flex backdrop-blur-2xl bg-white/30 p-2 rounded-[24px] border border-white/30 shadow-2xl shadow-black/5">
          <button
            onClick={() => setActiveTab("all")}
            className={`group relative px-8 py-3.5 rounded-[18px] text-sm font-semibold tracking-wide transition-all duration-500 ${
              activeTab === "all"
                ? "text-slate-800"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            {activeTab === "all" && (
              <div className="absolute inset-0 backdrop-blur-xl bg-white/70 rounded-[18px] shadow-xl shadow-black/10 border border-white/40"></div>
            )}
            <span className="relative z-10 flex items-center">
              <Newspaper size={16} className="mr-2" strokeWidth={1.5} />
              All News
            </span>
          </button>
          
          <button
            onClick={() => setActiveTab("popular")}
            className={`group relative px-8 py-3.5 rounded-[18px] text-sm font-semibold tracking-wide transition-all duration-500 ${
              activeTab === "popular"
                ? "text-orange-600"
                : "text-slate-500 hover:text-orange-500"
            }`}
          >
            {activeTab === "popular" && (
              <div className="absolute inset-0 backdrop-blur-xl bg-gradient-to-br from-orange-50/80 to-red-50/60 rounded-[18px] shadow-xl shadow-orange-500/20 border border-orange-200/40"></div>
            )}
            <span className="relative z-10 flex items-center">
              <Flame size={16} className="mr-2" strokeWidth={1.5} />
              Popular
            </span>
          </button>

          <button
            onClick={() => setActiveTab("favorites")}
            className={`group relative px-8 py-3.5 rounded-[18px] text-sm font-semibold tracking-wide transition-all duration-500 ${
              activeTab === "favorites"
                ? "text-amber-600"
                : "text-slate-500 hover:text-amber-500"
            }`}
          >
            {activeTab === "favorites" && (
              <div className="absolute inset-0 backdrop-blur-xl bg-gradient-to-br from-amber-50/80 to-yellow-50/60 rounded-[18px] shadow-xl shadow-amber-500/20 border border-amber-200/40"></div>
            )}
            <span className="relative z-10 flex items-center">
              <Star size={16} className="mr-2" strokeWidth={1.5} />
              Favorites
              <span className="ml-2 text-xs backdrop-blur-sm bg-white/40 px-2 py-0.5 rounded-full border border-white/30">
                {news.filter((n) => n.is_favorite).length}
              </span>
            </span>
          </button>
        </div>
      </div>

      {/* CONTENT */}
      <main className="max-w-7xl mx-auto px-8 pb-20">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-40">
            <div className="relative">
              <div className="absolute inset-0 backdrop-blur-xl bg-white/40 rounded-full blur-2xl"></div>
              <div className="relative w-20 h-20 backdrop-blur-xl bg-white/30 border-4 border-white/40 border-t-blue-400 rounded-full animate-spin shadow-2xl"></div>
            </div>
            <p className="mt-8 text-slate-600 font-medium tracking-wide">Loading Intelligence...</p>
          </div>
        ) : (
          <>
            {/* POPULAR TOPICS */}
            {activeTab === "popular" && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {topics.map((topic, index) => (
                  <div
                    key={topic.id}
                    className="group relative backdrop-blur-2xl bg-white/30 p-8 rounded-[32px] border border-white/30 shadow-2xl shadow-black/5 hover:shadow-orange-500/20 transition-all duration-700 hover:-translate-y-2"
                    style={{
                      animationDelay: `${index * 100}ms`,
                      animation: "floatIn 0.8s ease-out forwards",
                      opacity: 0,
                    }}
                  >
                    {/* Ambient Glow */}
                    <div className="absolute -inset-1 bg-gradient-to-br from-orange-400/10 via-red-400/5 to-pink-400/10 rounded-[34px] blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>

                    <div className="relative z-10">
                      <div className="flex items-center justify-between mb-5">
                        <div className="backdrop-blur-xl bg-gradient-to-br from-orange-50/60 to-red-50/40 px-4 py-2 rounded-[16px] border border-orange-200/30 shadow-lg shadow-orange-500/10">
                          <span className="flex items-center text-orange-600 text-xs font-bold tracking-wide">
                            <Sparkles size={14} className="mr-1.5" strokeWidth={2} />
                            Score {topic.popularity_score}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <TrendingUp size={16} className="text-orange-500" strokeWidth={1.5} />
                          <span className="text-xs font-semibold text-slate-600">
                            {topic.articles?.length || 0} sources
                          </span>
                        </div>
                      </div>

                      <h2 className="text-2xl font-semibold text-slate-800 leading-tight mb-4 group-hover:text-blue-600 transition-colors duration-300">
                        <a href={topic.url} target="_blank" rel="noopener noreferrer">
                          {topic.title}
                        </a>
                      </h2>

                      <p className="text-slate-600 line-clamp-3 text-sm leading-relaxed mb-6">
                        {stripHtml(topic.summary)}
                      </p>

                      <div className="flex items-center justify-between pt-5 border-t border-white/20">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedTopic(topic);
                          }}
                          className="group/btn relative backdrop-blur-xl bg-blue-50/60 hover:bg-blue-100/60 px-5 py-2.5 rounded-[14px] border border-blue-200/30 shadow-lg shadow-blue-500/10 transition-all duration-300 hover:scale-105"
                        >
                          <span className="flex items-center text-blue-600 text-sm font-semibold tracking-wide">
                            View Cluster
                            <span className="ml-2 backdrop-blur-sm bg-blue-600 text-white px-2.5 py-0.5 rounded-full text-xs font-bold">
                              {topic.articles?.length || 0}
                            </span>
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
                            className="backdrop-blur-xl bg-white/40 p-2.5 rounded-[12px] border border-white/30 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
                          >
                            <Share2 size={18} className="text-slate-600" strokeWidth={1.5} />
                          </button>

                          {openTopicMenuId === topic.id && (
                            <div className="absolute top-full right-0 mt-3 w-44 backdrop-blur-2xl bg-white/70 border border-white/30 rounded-[20px] shadow-2xl shadow-black/10 overflow-hidden">
                              {["LinkedIn", "WhatsApp", "Email"].map((platform) => (
                                <button
                                  key={platform}
                                  onClick={() => handleBroadcast(topic.id, platform, "topic")}
                                  className="w-full text-left px-5 py-3.5 text-slate-700 text-sm font-medium hover:bg-white/40 transition-colors duration-200"
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
                    className="group relative backdrop-blur-2xl bg-white/30 rounded-[28px] border border-white/30 shadow-2xl shadow-black/5 hover:shadow-blue-500/15 transition-all duration-700 hover:-translate-y-2 overflow-hidden"
                    style={{
                      animationDelay: `${index * 50}ms`,
                      animation: "floatIn 0.7s ease-out forwards",
                      opacity: 0,
                    }}
                  >
                    {/* Subtle Glow */}
                    <div className="absolute -inset-1 bg-gradient-to-br from-blue-400/10 via-indigo-400/5 to-purple-400/10 rounded-[30px] blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>

                    <div className="relative z-10 p-7">
                      <div className="flex justify-between items-center mb-4">
                        <span className="backdrop-blur-sm bg-blue-50/60 px-3 py-1.5 rounded-[10px] border border-blue-100/40 text-[10px] font-bold text-blue-600 uppercase tracking-wider truncate max-w-[70%]">
                          {item.source_name}
                        </span>
                        <div className="flex items-center space-x-1.5 text-xs text-slate-500">
                          <Clock size={12} strokeWidth={1.5} />
                          <span className="font-medium">{new Date(item.published_at).toLocaleDateString()}</span>
                        </div>
                      </div>

                      <h2 className="text-lg font-semibold text-slate-800 leading-tight mb-3 line-clamp-2 group-hover:text-blue-600 transition-colors duration-300">
                        <a href={item.url} target="_blank" rel="noopener noreferrer">
                          {item.title}
                        </a>
                      </h2>

                      <p className="text-sm text-slate-600 line-clamp-3 leading-relaxed mb-6">
                        {stripHtml(item.summary)}
                      </p>

                      <div className="flex items-center justify-between pt-5 border-t border-white/20">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => toggleFavorite(item.id)}
                            className={`backdrop-blur-xl p-2.5 rounded-[12px] border transition-all duration-300 hover:scale-110 ${
                              item.is_favorite
                                ? "bg-amber-50/60 border-amber-200/40 text-amber-500 shadow-lg shadow-amber-500/20"
                                : "bg-white/40 border-white/30 text-slate-400 hover:text-amber-500"
                            }`}
                          >
                            <Star
                              size={18}
                              fill={item.is_favorite ? "currentColor" : "none"}
                              strokeWidth={1.5}
                            />
                          </button>

                          <button
                            onClick={() => handleCopyLink(item.url)}
                            className="backdrop-blur-xl bg-white/40 p-2.5 rounded-[12px] border border-white/30 text-slate-400 hover:text-blue-500 hover:bg-blue-50/60 transition-all duration-300 hover:scale-110"
                          >
                            <LinkIcon size={18} strokeWidth={1.5} />
                          </button>
                        </div>

                        {item.is_favorite && (
                          <div className="relative">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setOpenMenuId(openMenuId === item.id ? null : item.id);
                              }}
                              className={`backdrop-blur-xl px-4 py-2 rounded-[12px] border text-xs font-semibold transition-all duration-300 ${
                                openMenuId === item.id
                                  ? "bg-slate-800 border-slate-700 text-white shadow-xl"
                                  : "bg-white/40 border-white/30 text-slate-600 hover:bg-slate-100/60"
                              }`}
                            >
                              <span className="flex items-center">
                                Share
                                <Share2 size={14} className="ml-1.5" strokeWidth={1.5} />
                              </span>
                            </button>

                            {openMenuId === item.id && (
                              <div className="absolute bottom-full right-0 mb-3 w-40 backdrop-blur-2xl bg-white/70 border border-white/30 rounded-[18px] shadow-2xl shadow-black/10 overflow-hidden">
                                {["LinkedIn", "WhatsApp", "Email"].map((platform) => (
                                  <button
                                    key={platform}
                                    onClick={() => handleBroadcast(item.id, platform, "news")}
                                    className="w-full text-left px-4 py-3 text-slate-700 text-xs font-medium hover:bg-white/40 transition-colors duration-200"
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
          className="fixed inset-0 z-50 flex items-center justify-center p-6"
          onClick={() => setSelectedTopic(null)}
        >
          {/* Backdrop */}
          <div className="absolute inset-0 backdrop-blur-2xl bg-slate-900/20 animate-fadeIn"></div>

          <div
            className="relative backdrop-blur-3xl bg-white/40 rounded-[40px] border border-white/30 shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden animate-scaleIn"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="relative p-10 border-b border-white/20">
              <div className="absolute inset-0 bg-gradient-to-br from-orange-50/30 via-transparent to-purple-50/20"></div>
              
              <div className="relative flex justify-between items-start">
                <div>
                  <div className="inline-flex items-center backdrop-blur-sm bg-orange-50/60 px-3 py-1.5 rounded-[12px] border border-orange-100/40 mb-3">
                    <Sparkles size={12} className="mr-1.5 text-orange-600" strokeWidth={2} />
                    <span className="text-xs font-bold text-orange-600 uppercase tracking-wider">
                      Topic Cluster
                    </span>
                  </div>
                  <h3 className="text-3xl font-semibold text-slate-800 leading-tight pr-12">
                    {selectedTopic.title}
                  </h3>
                </div>

                <button
                  onClick={() => setSelectedTopic(null)}
                  className="backdrop-blur-xl bg-white/40 p-3 rounded-[16px] border border-white/30 text-slate-600 hover:text-slate-900 hover:bg-white/60 shadow-lg transition-all duration-300 hover:rotate-90 hover:scale-110"
                >
                  <X size={20} strokeWidth={1.5} />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="overflow-y-auto p-10 space-y-5">
              {selectedTopic.articles.length > 0 ? (
                selectedTopic.articles.map((article, index) => (
                  <div
                    key={article.id}
                    className="group backdrop-blur-xl bg-white/30 p-6 rounded-[24px] border border-white/30 hover:bg-white/50 hover:shadow-xl transition-all duration-500"
                    style={{
                      animationDelay: `${index * 80}ms`,
                      animation: "floatIn 0.6s ease-out forwards",
                      opacity: 0,
                    }}
                  >
                    <div className="flex items-start">
                      <div className="mr-4 mt-2">
                        <div className="w-2 h-2 rounded-full bg-gradient-to-r from-blue-400 to-indigo-500 shadow-lg shadow-blue-400/50 group-hover:scale-125 transition-transform duration-300"></div>
                      </div>

                      <div className="flex-1">
                        <a
                          href={article.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-lg font-semibold text-slate-800 hover:text-blue-600 transition-colors duration-300 block mb-3"
                        >
                          {article.title}
                        </a>

                        <div className="flex items-center flex-wrap gap-3 text-xs text-slate-500">
                          <span className="backdrop-blur-sm bg-slate-100/60 px-3 py-1 rounded-[8px] font-medium border border-white/30">
                            Source #{article.source_id}
                          </span>
                          <span className="flex items-center space-x-1.5">
                            <Clock size={12} strokeWidth={1.5} />
                            <span className="font-medium">
                              {new Date(article.published_at).toLocaleDateString()}
                            </span>
                          </span>
                          <a
                            href={article.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center space-x-1 text-blue-600 hover:text-blue-700 font-semibold"
                          >
                            <span>Read</span>
                            <ExternalLink size={12} strokeWidth={1.5} />
                          </a>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-16">
                  <p className="text-slate-500 italic">
                    No additional articles found in this cluster.
                  </p>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-8 border-t border-white/20 text-center">
              <button
                onClick={() => setSelectedTopic(null)}
                className="backdrop-blur-xl bg-slate-800 hover:bg-slate-900 px-8 py-3.5 rounded-[16px] text-white font-semibold transition-all duration-300 hover:shadow-2xl hover:shadow-slate-900/30 hover:scale-105"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx global>{`
        @keyframes floatIn {
          from {
            opacity: 0;
            transform: translateY(30px) scale(0.95);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
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
          animation: scaleIn 0.4s ease-out;
        }

        /* Smooth scrolling */
        html {
          scroll-behavior: smooth;
        }

        /* Custom scrollbar for modal */
        ::-webkit-scrollbar {
          width: 8px;
        }

        ::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb {
          background: rgba(148, 163, 184, 0.3);
          border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb:hover {
          background: rgba(148, 163, 184, 0.5);
        }
      `}</style>
    </div>
  );
}

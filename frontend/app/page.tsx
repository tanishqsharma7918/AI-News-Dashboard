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
} from "lucide-react";

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
      const res = await fetch("http://localhost:8000/news");
      setNews(await res.json());
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const fetchTopics = async () => {
    try {
      const res = await fetch("http://localhost:8000/topics");
      setTopics(await res.json());
    } catch (err) {
      console.error(err);
    }
  };

  const toggleFavorite = async (id: number) => {
    setNews(
      news.map((item) =>
        item.id === id ? { ...item, is_favorite: !item.is_favorite } : item
      )
    );
    await fetch(`http://localhost:8000/news/${id}/favorite`, {
      method: "POST",
    });
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
      className="min-h-screen bg-slate-50 font-sans pb-20"
      onClick={handleGlobalClick}
    >
      {/* HEADER */}
      <header className="sticky top-0 z-50 bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-blue-600 p-1.5 rounded-lg">
              <Newspaper className="text-white" size={20} />
            </div>
            <h1 className="text-lg font-bold text-slate-900 tracking-tight">
              AI Pulse Dashboard
            </h1>
          </div>

          <button
            onClick={() => {
              fetchNews();
              fetchTopics();
            }}
            className="p-2 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-all"
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
              activeTab === "all"
                ? "bg-slate-900 text-white shadow"
                : "text-slate-600 hover:bg-slate-50"
            }`}
          >
            All News
          </button>
          <button
            onClick={() => setActiveTab("popular")}
            className={`px-5 py-2 rounded-md text-sm font-semibold transition-all flex items-center ${
              activeTab === "popular"
                ? "bg-orange-500 text-white shadow"
                : "text-slate-600 hover:bg-orange-50 hover:text-orange-600"
            }`}
          >
            <Flame size={16} className="mr-1.5" /> Popular
          </button>
          <button
            onClick={() => setActiveTab("favorites")}
            className={`px-5 py-2 rounded-md text-sm font-semibold transition-all ${
              activeTab === "favorites"
                ? "bg-slate-900 text-white shadow"
                : "text-slate-600 hover:bg-slate-50"
            }`}
          >
            Favorites ({news.filter((n) => n.is_favorite).length})
          </button>
        </div>
      </div>

      {/* CONTENT AREA */}
      <main className="max-w-6xl mx-auto px-6">
        {loading ? (
          <div className="text-center py-20 text-slate-500">
            Loading Intelligence...
          </div>
        ) : (
          <>
            {/* POPULAR TOPICS */}
            {activeTab === "popular" && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {topics.map((topic) => (
                  <div
                    key={topic.id}
                    className="bg-white p-6 rounded-xl border border-orange-100 shadow-sm hover:shadow-md transition-all relative"
                  >
                    <div className="absolute top-0 right-0 p-3 opacity-10">
                      <Flame size={100} className="text-orange-500" />
                    </div>

                    <span className="bg-orange-50 text-orange-700 px-3 py-1 rounded-full text-xs font-bold flex items-center border border-orange-100 w-fit">
                      <Sparkles size={12} className="mr-1" /> Score:{" "}
                      {topic.popularity_score}
                    </span>

                    <h2 className="text-xl font-bold text-slate-900 mt-3 hover:text-blue-600">
                      <a href={topic.url} target="_blank">
                        {topic.title}
                      </a>
                    </h2>

                    <p className="text-slate-600 mt-3 line-clamp-3 text-sm">
                      {stripHtml(topic.summary)}
                    </p>

                    <div className="mt-5 pt-4 border-t border-slate-100 flex space-x-4">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedTopic(topic);
                        }}
                        className="text-sm font-semibold text-blue-600"
                      >
                        View Cluster ({topic.articles?.length || 0})
                      </button>

                      <div className="relative">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setOpenTopicMenuId(
                              openTopicMenuId === topic.id ? null : topic.id
                            );
                          }}
                          className="text-sm font-semibold text-slate-500 flex items-center"
                        >
                          Share Topic <Share2 size={12} className="ml-1" />
                        </button>

                        {openTopicMenuId === topic.id && (
                          <div className="absolute top-full left-0 mt-2 w-36 bg-white border border-slate-200 rounded-lg shadow-xl z-50 overflow-hidden">
                            {["LinkedIn", "WhatsApp", "Email"].map(
                              (platform) => (
                                <button
                                  key={platform}
                                  onClick={() =>
                                    handleBroadcast(
                                      topic.id,
                                      platform,
                                      "topic"
                                    )
                                  }
                                  className="w-full text-left px-4 py-2 hover:bg-slate-50 text-slate-700 text-xs"
                                >
                                  {platform}
                                </button>
                              )
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* NEWS GRID */}
            {activeTab !== "popular" && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {displayedNews.map((item) => (
                  <div
                    key={item.id}
                    className="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-lg hover:border-blue-200 transition-all flex flex-col"
                  >
                    <div className="p-5 flex flex-col h-full">
                      <div className="flex justify-between items-center mb-3">
                        <span className="text-[11px] font-bold text-blue-600 uppercase truncate max-w-[70%]">
                          {item.source_name}
                        </span>
                        <span className="text-xs text-slate-400">
                          {new Date(
                            item.published_at
                          ).toLocaleDateString()}
                        </span>
                      </div>

                      <h2 className="text-base font-bold text-slate-900 mb-2 hover:text-blue-600">
                        <a href={item.url} target="_blank">
                          {item.title}
                        </a>
                      </h2>

                      <p className="text-sm text-slate-500 line-clamp-3">
                        {stripHtml(item.summary)}
                      </p>

                      <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between">
                        <div className="flex space-x-1">
                          <button
                            onClick={() => toggleFavorite(item.id)}
                            className={`p-2 rounded-md ${
                              item.is_favorite
                                ? "text-yellow-500 bg-yellow-50"
                                : "text-slate-400 hover:bg-slate-50"
                            }`}
                          >
                            <Star
                              size={18}
                              fill={
                                item.is_favorite ? "currentColor" : "none"
                              }
                            />
                          </button>

                          <button
                            onClick={() => handleCopyLink(item.url)}
                            className="p-2 rounded-md text-slate-400 hover:bg-slate-50 hover:text-blue-600"
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
                              className={`flex items-center space-x-1 px-3 py-1.5 rounded-md text-xs ${
                                openMenuId === item.id
                                  ? "bg-slate-900 text-white"
                                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                              }`}
                            >
                              <span>Share</span>
                              <Share2 size={14} />
                            </button>

                            {openMenuId === item.id && (
                              <div className="absolute bottom-full right-0 mb-2 w-32 bg-white border border-slate-200 rounded-lg shadow-xl z-50 overflow-hidden">
                                {["LinkedIn", "WhatsApp", "Email"].map(
                                  (platform) => (
                                    <button
                                      key={platform}
                                      onClick={() =>
                                        handleBroadcast(
                                          item.id,
                                          platform,
                                          "news"
                                        )
                                      }
                                      className="w-full text-left px-4 py-2 hover:bg-slate-50 text-slate-700 text-xs"
                                    >
                                      {platform}
                                    </button>
                                  )
                                )}
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
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm"
          onClick={() => setSelectedTopic(null)}
        >
          <div
            className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6 border-b border-slate-100 flex justify-between items-start bg-slate-50/50">
              <div>
                <span className="text-xs font-bold text-orange-600 uppercase tracking-wider block mb-1">
                  Topic Cluster
                </span>
                <h3 className="text-xl font-bold text-slate-900">
                  {selectedTopic.title}
                </h3>
              </div>

              <button
                onClick={() => setSelectedTopic(null)}
                className="p-2 bg-white hover:bg-slate-200 rounded-full text-slate-500"
              >
                <X size={20} />
              </button>
            </div>

            <div className="overflow-y-auto p-6 space-y-4">
              {selectedTopic.articles.length > 0 ? (
                selectedTopic.articles.map((article) => (
                  <div
                    key={article.id}
                    className="flex items-start group"
                  >
                    <div className="mr-4 mt-1.5">
                      <div className="w-2 h-2 rounded-full bg-blue-400 group-hover:bg-blue-600"></div>
                    </div>

                    <div>
                      <a
                        href={article.url}
                        target="_blank"
                        className="text-base font-semibold text-slate-800 hover:text-blue-600"
                      >
                        {article.title}
                      </a>

                      <div className="flex items-center mt-1 space-x-2 text-xs text-slate-400">
                        <span>Source #{article.source_id}</span>
                        <span>•</span>
                        <span>
                          {new Date(
                            article.published_at
                          ).toLocaleDateString()}
                        </span>
                        <span>•</span>

                        <a
                          href={article.url}
                          target="_blank"
                          className="flex items-center hover:text-blue-500"
                        >
                          Read <ExternalLink size={10} className="ml-1" />
                        </a>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-slate-500 italic">
                  No additional articles found in this cluster.
                </p>
              )}
            </div>

            <div className="p-4 border-t border-slate-100 bg-slate-50/50 text-center">
              <button
                onClick={() => setSelectedTopic(null)}
                className="text-sm font-semibold text-slate-500 hover:text-slate-800"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

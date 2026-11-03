import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ArrowRight, Search, SlidersHorizontal, ShoppingCart, Trash2, Plus, Minus, Heart, Package, ChartNoAxesCombined, Bell, Sparkles, Wallet, RefreshCw, LogIn, UserPlus, CheckCircle2, CircleAlert, ExternalLink } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, PieChart, Pie, Cell } from "recharts";
import api from "./api/client";
import { useAuth } from "./context/AuthContext";
import ProductCard from "./components/ProductCard";
import Notice from "./components/Notice";

const money = (v) => `₹${Number(v || 0).toLocaleString("en-IN", { maximumFractionDigits: 2 })}`;
const errMsg = (e) => e.response?.data?.detail || Object.values(e.response?.data || {}).flat().join(" ") || e.message || "Something went wrong.";
const COLORS = ["#a68bff", "#c9ff72", "#7bd9ff", "#ffad84", "#ff86bc", "#7ee0c3"];

function PageHeading({ eyebrow, title, text, action }) {
  return <div className="page-heading"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1>{text && <p>{text}</p>}</div>{action}</div>;
}
function EmptyState({ title, text, to = "/", action = "Browse products" }) {
  return <div className="empty-state"><div className="empty-symbol"><ShoppingCart size={25}/></div><h3>{title}</h3><p>{text}</p><Link className="button primary" to={to}>{action}<ArrowRight size={16}/></Link></div>;
}
function RequireLogin({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="loading-state">Loading your account…</div>;
  if (!user) return <EmptyState title="Sign in to continue" text="Create an account or sign in to access your personal shopping space." to="/login" action="Sign in"/>;
  return children;
}

export function HomePage() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [sort, setSort] = useState("-created_at");
  const [loading, setLoading] = useState(true);
  const [notice, setNotice] = useState(null);
  const [wishlistIds, setWishlistIds] = useState([]);
  const { user } = useAuth();

  async function loadProducts() {
    setLoading(true);
    try {
      const [p, c] = await Promise.all([
        api.get("/products/", { params: { search: search || undefined, category: category || undefined, ordering: sort } }),
        api.get("/categories/"),
      ]);
      setProducts(p.data.results || p.data);
      setCategories(c.data.results || c.data);
    } catch (e) { setNotice({type:"error", message:errMsg(e)}); }
    finally { setLoading(false); }
  }
  useEffect(() => { loadProducts(); }, [category, sort]);
  useEffect(() => {
    const timer = setTimeout(loadProducts, 250);
    return () => clearTimeout(timer);
  }, [search]);
  useEffect(() => {
    if (user) api.get("/wishlist/").then(r => setWishlistIds(r.data.map(x => x.product))).catch(() => {});
    else setWishlistIds([]);
  }, [user]);
  async function addToCart(product) {
    if (!user) { setNotice({type:"error", message:"Sign in before adding products to your cart."}); return; }
    try { await api.post("/cart/", {product:product.id, quantity:1}); setNotice({type:"success", message:`${product.name} added to your cart.`}); }
    catch (e) { setNotice({type:"error", message:errMsg(e)}); }
  }
  async function toggleWishlist(product) {
    if (!user) { setNotice({type:"error", message:"Sign in to save wishlist items."}); return; }
    try {
      const existing = await api.get("/wishlist/");
      const item = existing.data.find(x => x.product === product.id);
      if (item) { await api.delete(`/wishlist/${item.id}/`); setWishlistIds(old => old.filter(id => id !== product.id)); setNotice({type:"success", message:"Removed from wishlist."}); }
      else { await api.post("/wishlist/", {product:product.id}); setWishlistIds(old => [...old, product.id]); setNotice({type:"success", message:"Saved to wishlist."}); }
    } catch (e) { setNotice({type:"error", message:errMsg(e)}); }
  }
  return <div>
    <section className="hero-banner">
      <div className="hero-copy"><div className="eyebrow"><Sparkles size={14}/> A BETTER WAY TO BUY</div><h1>Shopping with<br/><span>your head</span> and heart.</h1><p>Find what fits your life, keep an eye on your spending, and make every purchase feel considered.</p><a className="button primary" href="#catalog">Explore the catalog <ArrowRight size={17}/></a><div className="hero-trust"><CheckCircle2 size={15}/> Transparent recommendations · Personal spending insights</div></div>
      <div className="hero-art"><div className="hero-ring ring-a"/><div className="hero-ring ring-b"/><div className="hero-art-card"><div className="art-top"><span className="art-label">THE CARTPILOT WAY</span><Sparkles size={20}/></div><div className="art-graphic"><div className="art-circle"><ShoppingCart size={43}/></div><span className="art-orbit-dot dot-a"/><span className="art-orbit-dot dot-b"/></div><div className="art-bottom"><div><b>Buy what matters.</b><small>Keep your goals in view.</small></div><span className="art-arrow"><ArrowRight size={18}/></span></div></div><div className="art-float float-one"><Wallet size={16}/> Budget-aware</div><div className="art-float float-two"><Sparkles size={16}/> Made for you</div></div>
    </section>
    {notice && <Notice {...notice} onClose={() => setNotice(null)}/>}
    <section className="catalog-section" id="catalog">
      <PageHeading eyebrow="THE COLLECTION" title="Find your next favorite." text="Thoughtful picks for your everyday life."/>
      <div className="catalog-tools"><label className="search-box"><Search size={18}/><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search products, categories, tags…"/></label><label className="select-wrap"><SlidersHorizontal size={16}/><select value={category} onChange={e=>setCategory(e.target.value)}><option value="">All categories</option>{categories.map(c=><option value={c.id} key={c.id}>{c.name}</option>)}</select></label><select className="sort-select" value={sort} onChange={e=>setSort(e.target.value)}><option value="-created_at">Newest first</option><option value="price">Price: low to high</option><option value="-price">Price: high to low</option><option value="name">Name A–Z</option></select></div>
      {loading ? <div className="loading-state"><RefreshCw className="spin" size={20}/> Loading products…</div> : products.length ? <div className="product-grid">{products.map(p=><ProductCard key={p.id} product={p} onAdd={addToCart} onWishlist={toggleWishlist} wishlisted={wishlistIds.includes(p.id)}/>)}</div> : <EmptyState title="No products found" text="Try a different search or category."/>}
    </section>
    <section className="value-strip"><div><Sparkles size={20}/><b>Recommendations with a reason</b><span>Discover products that fit your needs.</span></div><div><Wallet size={20}/><b>Spending in focus</b><span>Understand your shopping habits.</span></div><div><Bell size={20}/><b>Price watch</b><span>Set a target and keep an eye on it.</span></div></section>
  </div>;
}

export function ProductPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [notice, setNotice] = useState(null);
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [target, setTarget] = useState("");
  useEffect(() => { api.get(`/products/${id}/`).then(r=>setProduct(r.data)).catch(e=>setNotice({type:"error",message:errMsg(e)})); api.get("/reviews/",{params:{product:id}}).then(r=>setReviews(r.data.results||r.data)).catch(()=>{}); },[id]);
  async function addCart() { if (!user) return setNotice({type:"error",message:"Sign in to add items to your cart."}); try { await api.post("/cart/",{product:product.id,quantity:1}); setNotice({type:"success",message:"Added to cart."}); } catch(e){setNotice({type:"error",message:errMsg(e)});} }
  async function addWishlist() { if (!user) return setNotice({type:"error",message:"Sign in to save products."}); try { await api.post("/wishlist/",{product:product.id}); setNotice({type:"success",message:"Saved to wishlist."}); } catch(e){setNotice({type:"error",message:errMsg(e)});} }
  async function createAlert(e) { e.preventDefault(); try { await api.post("/price-alerts/",{product:product.id,target_price:target}); setNotice({type:"success",message:"Price target saved."}); setTarget(""); } catch(e){setNotice({type:"error",message:errMsg(e)});} }
  async function submitReview(e) { e.preventDefault(); try { await api.post("/reviews/",{product:product.id,rating,comment}); const r=await api.get("/reviews/",{params:{product:id}});setReviews(r.data.results||r.data);setComment("");setNotice({type:"success",message:"Review submitted."}); } catch(e){setNotice({type:"error",message:errMsg(e)});} }
  if (!product) return <div className="loading-state">Loading product…</div>;
  return <div className="detail-page"><Link className="back-link" to="/">← Back to catalog</Link>{notice&&<Notice {...notice} onClose={()=>setNotice(null)}/>}<div className="product-detail"><div className="detail-image">{product.image_url?<img src={product.image_url} alt={product.name}/>:<div className="detail-placeholder"><ShoppingCart size={70}/><span>{product.category_name}</span></div>}</div><div className="detail-copy"><div className="eyebrow">{product.category_name}</div><h1>{product.name}</h1><div className="detail-rating">★ {product.average_rating ?? "New"} <span>({product.review_count} reviews)</span></div><div className="detail-price">{money(product.price)}</div><p>{product.description || "A considered pick for everyday use."}</p><div className="stock-line"><span className={product.stock>0?"stock-green":"stock-red"}/>{product.stock>0?`${product.stock} available`:"Currently out of stock"}</div><div className="detail-actions"><button className="button primary" disabled={!product.stock} onClick={addCart}><ShoppingCart size={17}/> Add to cart</button><button className="button secondary" onClick={addWishlist}><Heart size={17}/> Wishlist</button></div><form className="inline-form price-alert-form" onSubmit={createAlert}><label>Target price</label><div><input type="number" min="0.01" step="0.01" value={target} onChange={e=>setTarget(e.target.value)} placeholder="e.g. 799" required/><button className="button secondary" type="submit"><Bell size={16}/> Set alert</button></div><small>We'll track CartPilot's recorded product price.</small></form></div></div><section className="reviews-section"><div className="section-title-row"><div><div className="eyebrow">COMMUNITY NOTES</div><h2>Reviews & ratings</h2></div></div>{user&&<form className="review-form" onSubmit={submitReview}><label>Your rating<select value={rating} onChange={e=>setRating(Number(e.target.value))}>{[5,4,3,2,1].map(n=><option key={n} value={n}>{n} stars</option>)}</select></label><label className="grow-label">Your review<textarea value={comment} onChange={e=>setComment(e.target.value)} placeholder="What should other shoppers know?" rows="3"/></label><button className="button primary" type="submit">Submit review</button></form>}{reviews.length?<div className="review-list">{reviews.map(r=><article className="review-card" key={r.id}><div><b>{r.username}</b><span className="review-stars">{"★".repeat(r.rating)}{"☆".repeat(5-r.rating)}</span></div><p>{r.comment||"Rated this product."}</p></article>)}</div>:<p className="muted-text">No reviews yet. Be the first to share your experience.</p>}</section></div>;
}

export function LoginPage({ register = false }) {
  const { login, register: signUp } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({username:"",email:"",first_name:"",last_name:"",password:"",password_confirm:""});
  const [busy,setBusy]=useState(false); const [error,setError]=useState("");
  function change(e){setForm({...form,[e.target.name]:e.target.value});}
  async function submit(e){e.preventDefault();setBusy(true);setError("");try{if(register)await signUp(form);else await login(form.username,form.password);navigate("/");}catch(e){setError(errMsg(e));}finally{setBusy(false);}}
  return <div className="auth-layout"><div className="auth-art"><div className="eyebrow">WELCOME TO CARTPILOT</div><h1>{register?"Start shopping with intention.":"Your smarter shopping space awaits."}</h1><p>Keep your favorites close, your plans clear, and your spending in view.</p><div className="auth-orbit"><ShoppingCart size={70}/></div></div><form className="auth-card" onSubmit={submit}><div className="auth-icon">{register?<UserPlus/>:<LogIn/>}</div><h2>{register?"Create your account":"Welcome back"}</h2><p>{register?"Your personal shopping assistant starts here.":"Sign in to continue your CartPilot journey."}</p>{error&&<Notice type="error" message={error}/>}<label>Username<input name="username" value={form.username} onChange={change} autoComplete="username" required/></label>{register&&<><label>Email<input name="email" type="email" value={form.email} onChange={change} required/></label><div className="two-inputs"><label>First name<input name="first_name" value={form.first_name} onChange={change}/></label><label>Last name<input name="last_name" value={form.last_name} onChange={change}/></label></div></>}<label>Password<input name="password" type="password" value={form.password} onChange={change} autoComplete={register?"new-password":"current-password"} required minLength="8"/></label>{register&&<label>Confirm password<input name="password_confirm" type="password" value={form.password_confirm} onChange={change} required minLength="8"/></label>}<button className="button primary full-button" disabled={busy}>{busy?"Please wait…":register?"Create account":"Sign in"}<ArrowRight size={16}/></button><div className="auth-switch">{register?"Already have an account?":"New to CartPilot?"} <Link to={register?"/login":"/register"}>{register?"Sign in":"Create account"}</Link></div></form></div>;
}

export function CartPage() {
  const [data,setData]=useState({items:[],subtotal:0,item_count:0});const [loading,setLoading]=useState(true);const [notice,setNotice]=useState(null);
  const [shipping,setShipping]=useState({shipping_name:"",shipping_phone:"",shipping_address:"",payment_method:"demo"});const navigate=useNavigate();
  async function load(){try{const r=await api.get("/cart/");setData(r.data);}catch(e){setNotice({type:"error",message:errMsg(e)});}finally{setLoading(false);}}
  useEffect(()=>{load();},[]);
  async function update(id,quantity){try{await api.patch(`/cart/items/${id}/`,{quantity});await load();}catch(e){setNotice({type:"error",message:errMsg(e)});}}
  async function remove(id){try{await api.delete(`/cart/items/${id}/`);await load();}catch(e){setNotice({type:"error",message:errMsg(e)});}}
  async function checkout(e){e.preventDefault();try{const r=await api.post("/checkout/",shipping);setNotice({type:"success",message:`Order #${r.data.id} placed successfully.`});await load();navigate("/orders");}catch(e){setNotice({type:"error",message:errMsg(e)});}}
  if(loading)return <div className="loading-state">Loading your cart…</div>;
  return <RequireLogin><PageHeading eyebrow="YOUR SELECTION" title="Shopping cart" text={`${data.item_count} item(s) ready when you are.`}/>{notice&&<Notice {...notice} onClose={()=>setNotice(null)}/>} {!data.items.length?<EmptyState title="Your cart is taking a breather" text="Find something useful and bring it here."/>:<div className="cart-layout"><div className="cart-items">{data.items.map(item=><article className="cart-row" key={item.id}><div className="cart-thumb">{item.product_detail.image_url?<img src={item.product_detail.image_url} alt=""/>:<ShoppingCart/>}</div><div className="cart-row-main"><Link to={`/products/${item.product}`}><b>{item.product_detail.name}</b></Link><span>{money(item.product_detail.price)} each</span><div className="quantity-control"><button onClick={()=>update(item.id,item.quantity-1)} disabled={item.quantity<=1}><Minus size={13}/></button><span>{item.quantity}</span><button onClick={()=>update(item.id,item.quantity+1)}><Plus size={13}/></button></div></div><div className="cart-row-end"><b>{money(item.line_total)}</b><button className="text-danger" onClick={()=>remove(item.id)}><Trash2 size={15}/> Remove</button></div></article>)}</div><aside className="checkout-panel"><div className="eyebrow">ORDER SUMMARY</div><div className="summary-line"><span>Subtotal</span><b>{money(data.subtotal)}</b></div><div className="summary-line"><span>Shipping</span><b>{Number(data.subtotal)>=1000?"Free":money(49)}</b></div><div className="summary-line total-line"><span>Total</span><b>{money(Number(data.subtotal)+(Number(data.subtotal)>=1000?0:49))}</b></div><p className="muted-text small">Free shipping on orders of ₹1,000 or more.</p><form className="checkout-form" onSubmit={checkout}><h3>Delivery details</h3><label>Full name<input value={shipping.shipping_name} onChange={e=>setShipping({...shipping,shipping_name:e.target.value})} required/></label><label>Phone number<input value={shipping.shipping_phone} onChange={e=>setShipping({...shipping,shipping_phone:e.target.value})} required/></label><label>Shipping address<textarea value={shipping.shipping_address} onChange={e=>setShipping({...shipping,shipping_address:e.target.value})} rows="3" required/></label><label>Payment method<select value={shipping.payment_method} onChange={e=>setShipping({...shipping,payment_method:e.target.value})}><option value="demo">Demo payment (no real charge)</option><option value="cod">Cash on delivery</option></select></label><button className="button primary full-button">Place test order <ArrowRight size={16}/></button></form></aside></div>}</RequireLogin>;
}

export function WishlistPage() {
  const [items,setItems]=useState([]);const [error,setError]=useState("");
  async function load(){try{const r=await api.get("/wishlist/");setItems(r.data);}catch(e){setError(errMsg(e));}}
  useEffect(()=>{load();},[]);
  async function remove(id){await api.delete(`/wishlist/${id}/`);load();}
  return <RequireLogin><PageHeading eyebrow="SAVED FOR LATER" title="Your wishlist" text="Good finds worth coming back to."/>{error&&<Notice type="error" message={error}/ >}{items.length?<div className="product-grid">{items.map(i=><ProductCard key={i.id} product={i.product_detail} onAdd={async p=>{try{await api.post("/cart/",{product:p.id,quantity:1});}catch(e){setError(errMsg(e));}}} onWishlist={()=>remove(i.product)} wishlisted/>)}</div>:<EmptyState title="Nothing saved yet" text="Tap the heart on a product to keep it close."/>}</RequireLogin>;
}

export function RecommendationsPage() {
  const [data,setData]=useState({reason:"",results:[]});const [error,setError]=useState("");
  useEffect(()=>{api.get("/recommendations/").then(r=>setData(r.data)).catch(e=>setError(errMsg(e)));},[]);
  return <><PageHeading eyebrow="A LITTLE MORE PERSONAL" title="Picked for your next move." text="Recommendations are generated from product categories, availability, and your shopping activity."/><div className="reason-banner"><Sparkles size={20}/><div><b>Why these picks?</b><span>{data.reason||"Finding useful products for you…"}</span></div></div>{error&&<Notice type="error" message={error}/ >}{data.results?.length?<div className="product-grid">{data.results.map(p=><ProductCard key={p.id} product={p} onAdd={async x=>{try{await api.post("/cart/",{product:x.id,quantity:1});}catch(e){setError(errMsg(e));}}} onWishlist={async x=>{try{await api.post("/wishlist/",{product:x.id});}catch(e){setError(errMsg(e));}}}/>)}</div>:<EmptyState title="No recommendations yet" text="Add products to the catalog to get started."/>}</>;
}

export function OrdersPage() {
  const [orders,setOrders]=useState([]);const [error,setError]=useState("");
  async function load(){try{const r=await api.get("/orders/");setOrders(r.data.results||r.data);}catch(e){setError(errMsg(e));}}
  useEffect(()=>{load();},[]);
  async function cancel(id){try{await api.post(`/orders/${id}/cancel/`);load();}catch(e){setError(errMsg(e));}}
  return <RequireLogin><PageHeading eyebrow="YOUR PURCHASES" title="Order history" text="Every order, in one place."/>{error&&<Notice type="error" message={error}/ >}{orders.length?<div className="order-list">{orders.map(o=><article className="order-card" key={o.id}><div className="order-card-top"><div><span className="muted-text small">ORDER #{o.id}</span><h3>{new Date(o.created_at).toLocaleDateString("en-IN",{day:"numeric",month:"short",year:"numeric"})}</h3></div><span className={`order-status status-${o.status}`}>{o.status}</span></div><div className="order-items-preview">{o.items.map(i=><div key={i.id}><span>{i.product_name} × {i.quantity}</span><b>{money(i.line_total)}</b></div>)}</div><div className="order-card-bottom"><span>{o.payment_method==="cod"?"Cash on delivery":"Demo payment"} · {o.payment_status}</span><b>{money(o.total)}</b>{["pending","confirmed"].includes(o.status)&&<button className="text-danger" onClick={()=>cancel(o.id)}>Cancel order</button>}</div></article>)}</div>:<EmptyState title="No orders yet" text="Your future great finds will show up here."/>}</RequireLogin>;
}

export function InsightsPage() {
  const [data,setData]=useState(null);const [budgets,setBudgets]=useState([]);const [amount,setAmount]=useState("");const [error,setError]=useState("");
  async function load(){try{const [d,b]=await Promise.all([api.get("/insights/summary/"),api.get("/budgets/")]);setData(d.data);setBudgets(b.data.results||b.data);}catch(e){setError(errMsg(e));}}
  useEffect(()=>{load();},[]);
  async function saveBudget(e){e.preventDefault();const month=new Date();const first=`${month.getFullYear()}-${String(month.getMonth()+1).padStart(2,"0")}-01`;try{const existing=budgets.find(b=>b.month===first);if(existing)await api.patch(`/budgets/${existing.id}/`,{amount});else await api.post("/budgets/",{month:first,amount});setAmount("");load();}catch(e){setError(errMsg(e));}}
  if(!data)return <RequireLogin><div className="loading-state">Loading insights…</div></RequireLogin>;
  const chartData=(data.spending_by_category||[]).map(x=>({category:x.category_name,amount:Number(x.total)}));
  return <RequireLogin><PageHeading eyebrow="YOUR SHOPPING, DECODED" title="Spending insights" text="Know where your money goes, without the guesswork."/><Notice type="info" message="Only confirmed, shipped, and delivered orders count as spending." />{error&&<Notice type="error" message={error}/ >}<div className="stats-grid"><div className="stat-card"><span className="stat-label">Spent this month</span><b>{money(data.spent_this_month)}</b><small>From eligible orders</small></div><div className="stat-card"><span className="stat-label">Monthly budget</span><b>{data.budget===null?"Not set":money(data.budget)}</b><small>{data.budget_remaining===null?"Set a budget below":`${money(Math.max(0,Number(data.budget_remaining)))} remaining`}</small></div><div className="stat-card"><span className="stat-label">Orders this month</span><b>{data.orders_this_month}</b><small>Current month</small></div><div className="stat-card"><span className="stat-label">All-time orders</span><b>{data.total_orders}</b><small>Eligible orders</small></div></div><div className="insights-grid"><section className="panel chart-panel"><div className="panel-heading"><div><div className="eyebrow">CATEGORY BREAKDOWN</div><h2>Where it goes</h2></div><ChartNoAxesCombined size={21}/></div>{chartData.length?<ResponsiveContainer width="100%" height={280}><BarChart data={chartData} margin={{top:10,right:10,left:0,bottom:10}}><CartesianGrid strokeDasharray="3 3" stroke="#ffffff12"/><XAxis dataKey="category" stroke="#9394aa" tick={{fontSize:11}}/><YAxis stroke="#9394aa" tick={{fontSize:11}}/><Tooltip contentStyle={{background:"#222338",border:"1px solid #ffffff20",borderRadius:10}} formatter={v=>money(v)}/><Bar dataKey="amount" fill="#a68bff" radius={[5,5,0,0]}/></BarChart></ResponsiveContainer>:<div className="chart-empty">Category insights will appear after your first order.</div>}</section><section className="panel budget-panel-full"><div className="panel-heading"><div><div className="eyebrow">STAY IN CONTROL</div><h2>Your monthly budget</h2></div><Wallet size={21}/></div><p className="muted-text">Choose a spending limit for this month. You can update it any time.</p><form onSubmit={saveBudget} className="budget-form"><label>Monthly budget (₹)<input type="number" min="0.01" step="0.01" value={amount} onChange={e=>setAmount(e.target.value)} placeholder={data.budget??"e.g. 5000"} required/></label><button className="button primary">Save budget</button></form>{data.budget!==null&&<div className="budget-progress"><div><span>Used</span><b>{Math.min(100,Math.round(Number(data.spent_this_month)/Math.max(Number(data.budget),1)*100))}%</b></div><div className="progress-track"><span style={{width:`${Math.min(100,Number(data.spent_this_month)/Math.max(Number(data.budget),1)*100)}%`}}/></div></div>}</section></div><section className="panel recent-panel"><div className="panel-heading"><div><div className="eyebrow">RECENT ACTIVITY</div><h2>Latest orders</h2></div><Link to="/orders" className="subtle-link">View all <ArrowRight size={15}/></Link></div>{data.recent_orders?.length?data.recent_orders.map(o=><div className="recent-order" key={o.id}><div className="recent-order-icon"><Package size={17}/></div><div className="recent-order-main"><b>Order #{o.id}</b><span>{new Date(o.created_at).toLocaleDateString("en-IN")} · {o.items.length} item(s)</span></div><span className={`order-status status-${o.status}`}>{o.status}</span><b>{money(o.total)}</b></div>):<p className="muted-text">Your completed shopping activity will appear here.</p>}</section></RequireLogin>;
}

export function PriceWatchPage() {
  const [items,setItems]=useState([]);const [error,setError]=useState("");
  async function load(){try{const r=await api.get("/price-alerts/");setItems(r.data.results||r.data);}catch(e){setError(errMsg(e));}}
  useEffect(()=>{load();},[]);
  async function remove(id){try{await api.delete(`/price-alerts/${id}/`);load();}catch(e){setError(errMsg(e));}}
  return <RequireLogin><PageHeading eyebrow="WAIT FOR THE RIGHT MOMENT" title="Your price watch" text="Keep track of target prices on products you care about."/>{error&&<Notice type="error" message={error}/ >}{items.length?<div className="price-watch-list">{items.map(a=><article className="price-watch-card" key={a.id}><div className="price-watch-icon"><Bell size={20}/></div><div className="price-watch-main"><b>{a.product_detail.name}</b><span>Current price: {money(a.current_price)} · Target: {money(a.target_price)}</span><small>{a.is_active?"Alert active":`Triggered ${a.triggered_at?new Date(a.triggered_at).toLocaleDateString():""}`}</small></div><span className={`order-status ${a.is_active?"status-confirmed":"status-delivered"}`}>{a.is_active?"Watching":"Triggered"}</span><button className="small-icon" onClick={()=>remove(a.id)} title="Delete alert"><Trash2 size={16}/></button></article>)}</div>:<EmptyState title="No price alerts yet" text="Open a product and set a target price to start tracking."/>}</RequireLogin>;
}

export function AdminDashboardPage() {
  const [data,setData]=useState(null);const [error,setError]=useState("");
  useEffect(()=>{api.get("/admin/analytics/").then(r=>setData(r.data)).catch(e=>setError(errMsg(e)));},[]);
  return <RequireLogin><PageHeading eyebrow="STORE OPERATIONS" title="Admin overview" text="A snapshot of the CartPilot catalog and store activity."/>{error&&<Notice type="error" message={error}/ >}{!data?<div className="loading-state">Loading admin analytics…</div>:<><div className="stats-grid"><div className="stat-card"><span className="stat-label">Products</span><b>{data.active_products}</b><small>{data.total_products} total</small></div><div className="stat-card"><span className="stat-label">Customers</span><b>{data.total_customers}</b><small>Registered accounts</small></div><div className="stat-card"><span className="stat-label">Orders</span><b>{data.total_orders}</b><small>All statuses</small></div><div className="stat-card"><span className="stat-label">Eligible revenue</span><b>{money(data.revenue)}</b><small>Confirmed, shipped, delivered</small></div></div><div className="admin-columns"><section className="panel"><div className="panel-heading"><h2>Order statuses</h2></div>{data.orders_by_status.map(x=><div className="summary-line" key={x.status}><span className={`order-status status-${x.status}`}>{x.status}</span><b>{x.count}</b></div>)}</section><section className="panel"><div className="panel-heading"><h2>Low stock</h2></div>{data.low_stock_products.length?data.low_stock_products.map(p=><div className="summary-line" key={p.id}><span>{p.name}</span><b className={p.stock===0?"text-danger":""}>{p.stock} left</b></div>):<p className="muted-text">No low-stock products.</p>}</section></div><section className="panel"><div className="panel-heading"><h2>Best sellers</h2></div>{data.best_sellers.map(p=><div className="summary-line" key={p.product_name}><span>{p.product_name}</span><b>{p.quantity_sold} sold · {money(p.revenue)}</b></div>)}</section><p className="muted-text small">Manage product and category records through Django Admin at <code>/admin/</code>. Catalog write APIs are restricted to staff users.</p></>}</RequireLogin>;
}

export function NotFoundPage(){return <EmptyState title="This page wandered off" text="That address doesn't match a CartPilot page."/>;}

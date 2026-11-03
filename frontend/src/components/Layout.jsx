import { NavLink, Link } from "react-router-dom";
import { Compass, ShoppingBag, Heart, Package, ChartNoAxesCombined, Bell, LogIn, LogOut, UserRound, Menu, X, ShoppingCart } from "lucide-react";import { useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const links = [
    ["/", "Shop", ShoppingBag],
    ["/cart", "Cart", ShoppingCart],
    ["/recommendations", "For you", Compass],
    ["/wishlist", "Wishlist", Heart],
    ["/orders", "Orders", Package],
    ["/insights", "Insights", ChartNoAxesCombined],
    ["/price-watch", "Price watch", Bell],
  ];
  return (
    <div className="app-layout">
      <header className="topbar">
        <Link to="/" className="brand"><span className="brand-mark"><Compass size={20}/></span><span>cartpilot<span className="brand-dot">.</span></span></Link>
        <button className="mobile-menu" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle menu">{menuOpen ? <X/> : <Menu/>}</button>
        <nav className={`nav-links ${menuOpen ? "nav-open" : ""}`}>
          {links.map(([to, label, Icon]) => <NavLink key={to} to={to} end={to === "/"} onClick={() => setMenuOpen(false)} className={({isActive}) => isActive ? "nav-item active" : "nav-item"}><Icon size={16}/>{label}</NavLink>)}
        </nav>
        <div className="account-area">
          {user ? <><span className="user-chip"><UserRound size={15}/>{user.first_name || user.username}</span><button className="icon-button" onClick={logout} title="Log out"><LogOut size={17}/></button>{user.is_staff && <Link className="staff-link" to="/admin-dashboard">Admin</Link>}</> : <Link className="login-link" to="/login"><LogIn size={16}/> Sign in</Link>}
        </div>
      </header>
      <main className="main-content">{children}</main>
      <footer className="site-footer"><span>© {new Date().getFullYear()} CartPilot</span><span>Shop smarter. Spend intentionally.</span><span className="footer-status"><i/> Django API powered</span></footer>
    </div>
  );
}

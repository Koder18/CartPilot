import { Link } from "react-router-dom";
import { Heart, ShoppingCart, Star } from "lucide-react";

export default function ProductCard({ product, onAdd, onWishlist, wishlisted = false }) {
  return (
    <article className="product-card">
      <Link to={`/products/${product.id}`} className="product-image-wrap">
        {product.image_url ? <img src={product.image_url} alt={product.name} loading="lazy" onError={(e) => { e.currentTarget.style.display = "none"; }} /> : <div className="product-placeholder"><ShoppingCart size={35}/><span>{product.category_name || "CartPilot pick"}</span></div>}
        <span className={`stock-pill ${product.stock > 0 ? "in-stock" : "out-stock"}`}>{product.stock > 0 ? "In stock" : "Sold out"}</span>
      </Link>
      <div className="product-card-body">
        <div className="product-category">{product.category_name || "Featured"}</div>
        <Link to={`/products/${product.id}`} className="product-name">{product.name}</Link>
        <div className="product-rating"><Star size={13} fill="currentColor"/>{product.average_rating ?? "New"} <span>({product.review_count ?? 0})</span></div>
        <div className="product-card-bottom"><strong>₹{Number(product.price).toLocaleString("en-IN")}</strong><div className="product-actions"><button className={`small-icon ${wishlisted ? "selected" : ""}`} title="Wishlist" onClick={() => onWishlist(product)}><Heart size={16} fill={wishlisted ? "currentColor" : "none"}/></button><button className="small-icon add-icon" title="Add to cart" disabled={!product.stock} onClick={() => onAdd(product)}><ShoppingCart size={16}/></button></div></div>
      </div>
    </article>
  );
}

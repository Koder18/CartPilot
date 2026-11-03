import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import {
  HomePage, ProductPage, LoginPage, CartPage, WishlistPage,
  RecommendationsPage, OrdersPage, InsightsPage, PriceWatchPage,
  AdminDashboardPage, NotFoundPage
} from "./pages";

export default function App() {
  return <Layout><Routes>
    <Route path="/" element={<HomePage/>}/>
    <Route path="/products/:id" element={<ProductPage/>}/>
    <Route path="/login" element={<LoginPage/>}/>
    <Route path="/register" element={<LoginPage register/>}/>
    <Route path="/cart" element={<CartPage/>}/>
    <Route path="/wishlist" element={<WishlistPage/>}/>
    <Route path="/recommendations" element={<RecommendationsPage/>}/>
    <Route path="/orders" element={<OrdersPage/>}/>
    <Route path="/insights" element={<InsightsPage/>}/>
    <Route path="/price-watch" element={<PriceWatchPage/>}/>
    <Route path="/admin-dashboard" element={<AdminDashboardPage/>}/>
    <Route path="*" element={<NotFoundPage/>}/>
  </Routes></Layout>;
}

export const localhost = "http://127.0.0.1:8000";

const apiURL = "/api";

export const endpoint = `${localhost}${apiURL}`;

export const userIDURL = `${endpoint}/user-id/`;
export const searchURL = `${endpoint}/searcha/`;
export const productListURL = `${endpoint}/products/`;
export const paymentListURL = `${endpoint}/payments/`;
export const productDetaiURL = (id) => `${endpoint}/products/${id}`;
export const designerDetaiURL = (id) => `${endpoint}/designer/${id}`;
export const addToCartURL = `${endpoint}/add-to-cart/`;
export const minusQuantityURL = `${endpoint}/order-items/minus-quantity/`;
export const orderSummaryURL = `${endpoint}/order-summary/`;
export const cheackoutURL = `${endpoint}/checkout/`;
export const addCouponURL = `${endpoint}/add-coupon/`;
export const countryListURL = `${endpoint}/countries/`;
export const addressListURL = (address_type) =>
  `${endpoint}/addresses/?address_type=${address_type}`;

export const addressCreateURL = `${endpoint}/addresses/create/`;
export const addressUpdateURL = (id) => `${endpoint}/addresses/${id}/update/`;
export const addressDeleteURL = (id) => `${endpoint}/addresses/${id}/delete/`;
export const OrderItemDeleteURL = (id) =>
  `${endpoint}/order-items/${id}/delete/`;

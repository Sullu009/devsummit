export type UserRole = "ATTENDEE" | "ORGANIZER" | "ADMIN";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  phone: string | null;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export type EventStatus = "DRAFT" | "PUBLISHED" | "CANCELLED";
export type EventCategory = "MUSIC" | "TECH" | "BUSINESS" | "ARTS" | "SPORTS" | "FOOD" | "COMMUNITY" | "OTHER";

export interface TicketType {
  id: string;
  name: string;
  description: string;
  price: string;
  quantity_total: number;
  quantity_available: number;
  sale_starts_at: string;
  sale_ends_at: string;
}

export interface Track {
  id: string;
  event_id: string;
  name: string;
  description: string;
  room_location: string;
  color_code: string;
  order: number;
}

export interface Speaker {
  id: string;
  event_id: string;
  name: string;
  role_title: string;
  company: string;
  bio: string;
  avatar_url: string;
  github_url?: string | null;
  twitter_url?: string | null;
  linkedin_url?: string | null;
  sessions?: Session[];
}

export interface Session {
  id: string;
  event_id: string;
  track_id: string | null;
  speaker_id: string | null;
  title: string;
  abstract: string;
  session_type: "KEYNOTE" | "TALK" | "WORKSHOP" | "PANEL" | "LIGHTNING";
  start_time: string;
  end_time: string;
  slides_url?: string | null;
  track?: Track | null;
  speaker?: Speaker | null;
}

export interface ScheduleSlot {
  time_label: string;
  start_time: string;
  end_time: string;
  sessions: Session[];
}

export interface ScheduleDay {
  date: string;
  date_label: string;
  tracks: Track[];
  slots: ScheduleSlot[];
}

export interface FullSchedule {
  event_id: string;
  event_title: string;
  days: ScheduleDay[];
}

export interface EventDetail {
  id: string;
  organizer_id: string;
  title: string;
  slug: string;
  description: string;
  category: EventCategory;
  status: EventStatus;
  cover_image_url: string | null;
  venue_name: string;
  venue_address: string;
  city: string;
  starts_at: string;
  ends_at: string;
  created_at: string;
  ticket_types: TicketType[];
  tracks?: Track[];
  speakers?: Speaker[];
  sessions?: Session[];
}

export interface EventSummary {
  id: string;
  organizer_id: string;
  title: string;
  slug: string;
  category: EventCategory;
  status: EventStatus;
  cover_image_url: string | null;
  city: string;
  starts_at: string;
  min_price: string | null;
  max_price: string | null;
}

export interface PaginatedEvents {
  items: EventSummary[];
  total: number;
  page: number;
  page_size: number;
}

export type BookingStatus = "PENDING_PAYMENT" | "CONFIRMED" | "CANCELLED" | "EXPIRED" | "REFUND_PENDING" | "REFUNDED";

export interface BookingItem {
  id: string;
  ticket_type_id: string;
  ticket_type_name: string;
  unit_price: string;
  quantity: number;
}

export interface Booking {
  id: string;
  reservation_id: string;
  user_id: string;
  event_id: string;
  organizer_id: string;
  status: BookingStatus;
  total_amount: string;
  expires_at: string | null;
  created_at: string;
  items: BookingItem[];
}

export type PaymentStatus = "CREATED" | "SUCCEEDED" | "FAILED" | "REFUNDED";

export interface Payment {
  id: string;
  booking_id: string;
  user_id: string;
  organizer_id: string;
  event_id: string;
  razorpay_order_id: string;
  razorpay_payment_id: string | null;
  amount: string;
  currency: string;
  status: PaymentStatus;
  failure_reason: string | null;
  created_at: string;
}

export interface EventRevenue {
  event_id: string;
  gross_revenue: number;
  net_revenue: number;
  paid_bookings: number;
  refunded_count: number;
  refunded_amount: number;
  payment_failures: number;
  payment_success_rate: number;
  recent_transactions: Payment[];
}

export interface EventAnalytics {
  event_id: string;
  views: number;
  bookings_created: number;
  bookings_confirmed: number;
  bookings_cancelled: number;
  tickets_sold: number;
  revenue: number;
  attendance_count: number;
  conversion_rate: number;
}

export interface NotificationItem {
  id: string;
  type: string;
  title: string;
  body: string;
  is_read: boolean;
  created_at: string;
}

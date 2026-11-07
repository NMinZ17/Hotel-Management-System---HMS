-- Co so va phong

CREATE TABLE room_type (
    room_type_id BIGINT PRIMARY KEY,
    name VARCHAR(80),
    max_guests SMALLINT,
    base_price NUMERIC(14,2),
    is_active BOOLEAN
);

CREATE TABLE hotel (
    hotel_id SMALLINT PRIMARY KEY,
    name VARCHAR(150),
    address TEXT,
    phone VARCHAR(30),
    timezone VARCHAR(50)
);

CREATE TABLE amenity (
    amenity_id BIGINT PRIMARY KEY,
    name VARCHAR(80)
);

CREATE TABLE room (
    room_id BIGINT PRIMARY KEY,
    room_type_id BIGINT REFERENCES room_type(room_type_id),
    room_number VARCHAR(15),
    floor SMALLINT,
    housekeeping_status VARCHAR(15),
    maintenance_status VARCHAR(15),
    is_active BOOLEAN
);

CREATE TABLE room_amenity (
    room_id BIGINT,
    amenity_id BIGINT,
    PRIMARY KEY (room_id, amenity_id),
    CONSTRAINT fk_room_amenity_room FOREIGN KEY (room_id) REFERENCES room(room_id) ON DELETE CASCADE,
    CONSTRAINT fk_room_amenity_amenity FOREIGN KEY (amenity_id) REFERENCES amenity(amenity_id) ON DELETE CASCADE
);

-- Tai khoan va con nguoi

CREATE TABLE role (
    role_id SMALLINT PRIMARY KEY,
    code VARCHAR(10),
    name VARCHAR(80)
);

CREATE TABLE app_user (
    user_id BIGINT PRIMARY KEY,
    email VARCHAR(254),
    password_hash TEXT,
    is_active BOOLEAN,
    created_at TIMESTAMPTZ
);

CREATE TABLE user_role (
    user_id BIGINT,
    role_id SMALLINT,
    PRIMARY KEY (user_id, role_id),
    CONSTRAINT fk_user_role_user FOREIGN KEY (user_id) REFERENCES app_user(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_user_role_role FOREIGN KEY (role_id) REFERENCES role(role_id) ON DELETE CASCADE
);

CREATE TABLE guest (
    guest_id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES app_user(user_id),
    full_name VARCHAR(120),
    phone VARCHAR(30),
    email VARCHAR(254)
);

CREATE TABLE employee (
    employee_id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES app_user(user_id),
    full_name VARCHAR(120),
    job_title VARCHAR(80),
    is_active BOOLEAN
);

-- Dat phong

CREATE TABLE discount (
    discount_id BIGINT PRIMARY KEY,
    code VARCHAR(30),
    discount_type VARCHAR(10),
    value NUMERIC(14,2),
    valid_from DATE,
    valid_to DATE,
    is_active BOOLEAN
);

CREATE TABLE reservation (
    reservation_id BIGINT PRIMARY KEY,
    booked_by_guest_id BIGINT REFERENCES guest(guest_id),
    status VARCHAR(15),
    created_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    note VARCHAR(200)
);

CREATE TABLE reservation_room (
    reservation_room_id BIGINT PRIMARY KEY,
    reservation_id BIGINT REFERENCES reservation(reservation_id) ON DELETE CASCADE,
    room_id BIGINT REFERENCES room(room_id),
    check_in_date DATE,
    check_out_date DATE,
    adults SMALLINT,
    children SMALLINT,
    nightly_price NUMERIC(14,2),
    is_cancelled BOOLEAN
);

CREATE TABLE reservation_guest (
    reservation_id BIGINT,
    guest_id BIGINT,
    is_primary BOOLEAN,
    PRIMARY KEY (reservation_id, guest_id),
    CONSTRAINT fk_reservation_guest_reservation FOREIGN KEY (reservation_id) REFERENCES reservation(reservation_id) ON DELETE CASCADE,
    CONSTRAINT fk_reservation_guest_guest FOREIGN KEY (guest_id) REFERENCES guest(guest_id) ON DELETE CASCADE
);

CREATE TABLE reservation_discount (
    reservation_id BIGINT PRIMARY KEY REFERENCES reservation(reservation_id) ON DELETE CASCADE,
    discount_id BIGINT REFERENCES discount(discount_id),
    discount_amount NUMERIC(14,2)
);

-- Luu tru va tai chinh

CREATE TABLE stay (
    stay_id BIGINT PRIMARY KEY,
    reservation_id BIGINT REFERENCES reservation(reservation_id),
    checked_in_by BIGINT REFERENCES employee(employee_id),
    checked_out_by BIGINT REFERENCES employee(employee_id),
    actual_check_in TIMESTAMPTZ,
    actual_check_out TIMESTAMPTZ,
    status VARCHAR(15)
);

CREATE TABLE stay_room (
    stay_room_id BIGINT PRIMARY KEY,
    stay_id BIGINT REFERENCES stay(stay_id) ON DELETE CASCADE,
    reservation_room_id BIGINT REFERENCES reservation_room(reservation_room_id),
    room_id BIGINT REFERENCES room(room_id),
    assigned_from TIMESTAMPTZ,
    assigned_to TIMESTAMPTZ
);

CREATE TABLE folio (
    folio_id BIGINT PRIMARY KEY,
    stay_id BIGINT REFERENCES stay(stay_id) ON DELETE CASCADE,
    status VARCHAR(10),
    opened_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ
);

CREATE TABLE folio_item (
    folio_item_id BIGINT PRIMARY KEY,
    folio_id BIGINT REFERENCES folio(folio_id) ON DELETE CASCADE,
    entry_type VARCHAR(10),
    description VARCHAR(200),
    quantity NUMERIC(10,2),
    unit_price NUMERIC(14,2),
    source_key VARCHAR(120),
    occurred_at TIMESTAMPTZ
);

CREATE TABLE invoice (
    invoice_id BIGINT PRIMARY KEY,
    folio_id BIGINT REFERENCES folio(folio_id),
    invoice_number VARCHAR(40),
    subtotal NUMERIC(14,2),
    discount_total NUMERIC(14,2),
    tax_amount NUMERIC(14,2),
    issued_at TIMESTAMPTZ,
    status VARCHAR(10)
);

CREATE TABLE payment (
    payment_id BIGINT PRIMARY KEY,
    invoice_id BIGINT REFERENCES invoice(invoice_id) ON DELETE CASCADE,
    recorded_by BIGINT REFERENCES employee(employee_id),
    amount NUMERIC(14,2),
    method VARCHAR(15),
    transaction_ref VARCHAR(80),
    paid_at TIMESTAMPTZ
);

CREATE TABLE service (
    service_id BIGINT PRIMARY KEY,
    name VARCHAR(120),
    category VARCHAR(15),
    unit_price NUMERIC(14,2),
    is_active BOOLEAN
);

CREATE TABLE housekeeping_task (
    task_id BIGINT PRIMARY KEY,
    room_id BIGINT REFERENCES room(room_id),
    assigned_to BIGINT REFERENCES employee(employee_id),
    scheduled_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    status VARCHAR(15)
);

CREATE TABLE maintenance_ticket (
    ticket_id BIGINT PRIMARY KEY,
    room_id BIGINT REFERENCES room(room_id),
    reported_by BIGINT REFERENCES employee(employee_id),
    assigned_to BIGINT REFERENCES employee(employee_id),
    description VARCHAR(200),
    status VARCHAR(15),
    reported_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ
);

CREATE TABLE service_order (
    service_order_id BIGINT PRIMARY KEY,
    stay_room_id BIGINT REFERENCES stay_room(stay_room_id),
    assigned_to BIGINT REFERENCES employee(employee_id),
    status VARCHAR(15),
    ordered_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE TABLE service_order_item (
    service_order_item_id BIGINT PRIMARY KEY,
    service_order_id BIGINT REFERENCES service_order(service_order_id) ON DELETE CASCADE,
    service_id BIGINT REFERENCES service(service_id),
    quantity NUMERIC(10,2),
    unit_price NUMERIC(14,2),
    folio_item_id BIGINT REFERENCES folio_item(folio_item_id)
);

CREATE TABLE guest_review (
    review_id BIGINT PRIMARY KEY,
    stay_id BIGINT REFERENCES stay(stay_id),
    guest_id BIGINT REFERENCES guest(guest_id),
    rating SMALLINT,
    comment VARCHAR(1000),
    created_at TIMESTAMPTZ
);

CREATE TABLE audit_event (
    event_id BIGINT PRIMARY KEY,
    actor_user_id BIGINT REFERENCES app_user(user_id),
    reservation_id BIGINT REFERENCES reservation(reservation_id),
    service_order_id BIGINT REFERENCES service_order(service_order_id),
    action VARCHAR(40),
    details JSONB,
    occurred_at TIMESTAMPTZ
);
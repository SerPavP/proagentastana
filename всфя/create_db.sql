CREATE DATABASE proagentastana;
USE proagentastana;
-- 1. Агентства
CREATE TABLE agencies (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Пользователи
CREATE TABLE users (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  full_name     VARCHAR(255) NOT NULL,
  phone         VARCHAR(20)  NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  photo_url     VARCHAR(512),
  agency_id     INT,
  is_active     BOOLEAN     NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP   DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (agency_id) REFERENCES agencies(id)
);

-- 3. Тарифы (для будущего)
CREATE TABLE tariffs (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  name         VARCHAR(100) NOT NULL,
  price        DECIMAL(10,2) NOT NULL,
  duration_days INT         NOT NULL,  -- длительность подписки
  created_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- 4. Подписки пользователей
CREATE TABLE subscriptions (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT NOT NULL,
  tariff_id  INT NOT NULL,
  start_date DATE NOT NULL,
  end_date   DATE NOT NULL,
  active     BOOLEAN DEFAULT TRUE,
  FOREIGN KEY (user_id)   REFERENCES users(id),
  FOREIGN KEY (tariff_id) REFERENCES tariffs(id)
);

-- 5. Адреса квартир
CREATE TABLE addresses (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  microdistrict  VARCHAR(100),
  complex_name   VARCHAR(100),
  street         VARCHAR(255),
  building_no    VARCHAR(50),
  latitude       DECIMAL(9,6),
  longitude      DECIMAL(9,6)
);

-- 6. Объявления
CREATE TABLE announcements (
  id               INT AUTO_INCREMENT PRIMARY KEY,
  user_id          INT NOT NULL,
  address_id       INT NOT NULL,
  rooms_count      TINYINT NOT NULL,
  price            BIGINT  NOT NULL,
  repair_status    ENUM(
                      'Черновая отделка',
                      'Новый ремонт',
                      'Аккуратный ремонт',
                      'Старый ремонт'
                    ) NOT NULL,
  building_type    VARCHAR(50),
  year_built       YEAR,
  is_new_building  BOOLEAN DEFAULT FALSE,
  floor            SMALLINT,
  total_floors     SMALLINT,
  area             DECIMAL(7,2) NOT NULL,
  description      TEXT,
  is_archived      BOOLEAN DEFAULT FALSE,
  created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id)    REFERENCES users(id),
  FOREIGN KEY (address_id) REFERENCES addresses(id)
);

-- 7. Фотографии объявлений
CREATE TABLE photos (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  announcement_id INT NOT NULL,
  url             VARCHAR(512) NOT NULL,
  is_main         BOOLEAN DEFAULT FALSE,
  uploaded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (announcement_id) REFERENCES announcements(id)
);

-- 8. Подборки квартир
CREATE TABLE collections (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT NOT NULL,
  name       VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 9. Связующая таблица подборок и объявлений
CREATE TABLE collection_items (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  collection_id   INT NOT NULL,
  announcement_id INT NOT NULL,
  added_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (collection_id)   REFERENCES collections(id) ON DELETE CASCADE,
  FOREIGN KEY (announcement_id) REFERENCES announcements(id) ON DELETE CASCADE
);

-- 10. Лог сессий пользователей
CREATE TABLE user_sessions (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NOT NULL,
  session_key  VARCHAR(40) NOT NULL,
  login_time   DATETIME NOT NULL,
  logout_time  DATETIME,
  duration     TIME,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 11. Просмотры страниц (опционально)
CREATE TABLE page_views (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  user_id   INT NOT NULL,
  path      VARCHAR(255) NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  duration_seconds INT,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

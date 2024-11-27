DROP DATABASE  IF EXISTS catfeeder;
CREATE DATABASE  IF NOT EXISTS catfeeder;
USE catfeeder;


CREATE TABLE `family` (
  `id` integer NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `name` varchar(255),
  `registered_at` timestamp
);

CREATE TABLE `users` (
  `id` integer NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `email` varchar(255),
  `name` varchar(255),
  `disabled` bool,
  `hashed_password` varchar(255),
  `family_id` integer,
  `family_admin` bool,
  `registered_at` timestamp
);

CREATE TABLE `feeders` (
  `id` integer NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `type` integer,
  `name` varchar(255),
  `max_meal` integer,
  `current_meal` integer,
  `portion_meal` integer,
  `user_id` integer,
  `configured` bool,
  `registered_at` timestamp
);

CREATE TABLE `schedules` (
  `id` integer NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `feeder_id` integer,
  `value` varchar(255)
);

CREATE TABLE `tags` (
  `id` integer NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `feeder_id` integer,
  `value` varchar(255)
);

CREATE TABLE `logs` (
  `id` integer NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `family_id` integer,
  `feeder_id` integer,
  `user_id` integer,
   `meal_poured` integer,
  `log`  varchar(255),
  `registered_at` timestamp
);

ALTER TABLE `users` ADD FOREIGN KEY (`family_id`) REFERENCES `family` (`id`);

ALTER TABLE `feeders` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `schedules` ADD FOREIGN KEY (`feeder_id`) REFERENCES `feeders` (`id`);

ALTER TABLE `tags` ADD FOREIGN KEY (`feeder_id`) REFERENCES `feeders` (`id`);

ALTER TABLE `logs` ADD FOREIGN KEY (`feeder_id`) REFERENCES `feeders` (`id`);

ALTER TABLE `logs` ADD FOREIGN KEY (`family_id`) REFERENCES `family` (`id`);

ALTER TABLE `logs` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);



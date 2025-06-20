-- 以下内容是本项目数据库结构与实际操作的示意SQL语句，注意该文件只是用作本项目涉及的数据库操作概念展示，
-- 实际操作已经嵌入Python代码，所以本文件不是运行项目的必须文件。建表语句SQL在第10部分。
DROP DATABASE samp_db;
CREATE DATABASE samp_db;
use samp_db;-- 在这里变成你本机的数据库名称。

-- -----------------------------
-- 1. 主页面统计 main_view
-- -----------------------------
SELECT COUNT(*) FROM crawls_website;

SELECT COUNT(*) FROM crawls_webpage;

SELECT COUNT(*) FROM crawls_content;

-- -----------------------------
-- 2. 新增爬虫任务 user_input_view
-- -----------------------------
-- 查询网站是否已存在
SELECT *
FROM crawls_website
WHERE
    user_id = < user_id >
    AND domain = '<domain>';

-- 若不存在则插入
INSERT INTO
    crawls_website (domain, user_id)
VALUES ('<domain>', < user_id >);

-- 插入爬取任务记录
INSERT INTO
    crawls_crawltask (
        status,
        start_time,
        user_id,
        website_id
    )
VALUES (
        'crawling',
        CURRENT_TIMESTAMP,
        < user_id >,
        < website_id >
    );

-- -----------------------------
-- 3. 展示已完成爬取网站 recent_websites
-- -----------------------------
-- 管理员视角
SELECT w.*, COUNT(DISTINCT p.id) AS page_count
FROM
    crawls_website w
    JOIN crawls_crawltask t ON w.id = t.website_id
    LEFT JOIN crawls_webpage p ON w.id = p.website_id
WHERE
    t.status = 'complete'
GROUP BY
    w.id
ORDER BY w.domain DESC;

-- 普通用户视角
SELECT w.*, COUNT(DISTINCT p.id) AS page_count
FROM
    crawls_website w
    JOIN crawls_crawltask t ON w.id = t.website_id
    LEFT JOIN crawls_webpage p ON w.id = p.website_id
WHERE
    t.status = 'complete'
    AND w.user_id = < user_id >
GROUP BY
    w.id
ORDER BY w.domain DESC;

-- -----------------------------
-- 4. 删除网站 delete_webstie_view
-- -----------------------------
-- 删除图片相关数据源
DELETE FROM crawls_datasource
WHERE
    data_source_url IN (
        SELECT url
        FROM crawls_image
        WHERE
            webpage_id IN (
                SELECT id
                FROM crawls_webpage
                WHERE
                    website_id = < website_id >
            )
    );

-- 删除网页对应数据源
DELETE FROM crawls_datasource
WHERE
    data_source_url IN (
        SELECT url
        FROM crawls_webpage
        WHERE
            website_id = < website_id >
    );

-- 删除网页内容与图片
DELETE FROM crawls_content
WHERE
    webpage_id IN (
        SELECT id
        FROM crawls_webpage
        WHERE
            website_id = < website_id >
    );

DELETE FROM crawls_image
WHERE
    webpage_id IN (
        SELECT id
        FROM crawls_webpage
        WHERE
            website_id = < website_id >
    );

-- 删除网页
DELETE FROM crawls_webpage WHERE website_id = < website_id >;

-- 删除网站
DELETE FROM crawls_website WHERE id = < website_id >;

-- -----------------------------
-- 5. 删除网页 delete_webpage_view
-- -----------------------------
DELETE FROM crawls_datasource
WHERE
    data_source_url = '<webpage_url>';

DELETE FROM crawls_datasource
WHERE
    data_source_url IN (
        SELECT url
        FROM crawls_image
        WHERE
            webpage_id = < webpage_id >
    );

DELETE FROM crawls_content WHERE webpage_id = < webpage_id >;

DELETE FROM crawls_image WHERE webpage_id = < webpage_id >;

DELETE FROM crawls_webpage WHERE id = < webpage_id >;

-- -----------------------------
-- 6. 删除内容 delete_content_view
-- -----------------------------
DELETE FROM crawls_content WHERE content_id = < content_id >;

DELETE FROM crawls_datasource
WHERE
    data_source_url = (
        SELECT url
        FROM crawls_webpage
        WHERE
            id = (
                SELECT webpage_id
                FROM crawls_content
                WHERE
                    content_id = < content_id >
            )
    );

-- -----------------------------
-- 7. 删除图片 delete_image_view
-- -----------------------------
DELETE FROM crawls_image WHERE url_id = '<url>';

DELETE FROM crawls_datasource WHERE data_source_url = '<url>';

-- -----------------------------
-- 8. 搜索内容 search_content_view
-- -----------------------------
-- 管理员
SELECT * FROM crawls_content WHERE keywords LIKE '%<query>%';

-- 普通用户
SELECT c.*
FROM
    crawls_content c
    JOIN crawls_webpage w ON c.webpage_id = w.id
    JOIN crawls_website s ON w.website_id = s.id
WHERE
    c.keywords LIKE '%<query>%'
    AND s.user_id = < user_id >;

-- -----------------------------
-- 9. 查询页面、图片、内容
-- -----------------------------
-- 某网站所有网页
SELECT *
FROM crawls_webpage
WHERE
    website_id = < site_id >
ORDER BY crawl_time DESC;

-- 某网页所有图片
SELECT * FROM crawls_image WHERE webpage_id = < page_id >;

-- 某网页所有内容
SELECT * FROM crawls_content WHERE webpage_id = < page_id >;

-- -----------------------------
-- 10. migrations 自动的建表SQL语句
-- -----------------------------
-- Create model DataSource
CREATE TABLE `crawls_datasource` (
    `data_source_url` varchar(500) NOT NULL PRIMARY KEY,
    `publisher` varchar(100) NULL,
    `publish_time` datetime(6) NULL
);

-- Create model Webpage
CREATE TABLE `crawls_webpage` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `url` varchar(500) NOT NULL,
    `crawl_time` datetime(6) NOT NULL
);

-- Create model Content
CREATE TABLE `crawls_content` (
    `content_id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `text` longtext NOT NULL,
    `keywords` varchar(500) NOT NULL,
    `type` varchar(10) NOT NULL,
    `webpage_id` integer NOT NULL
);

-- Create model Website
CREATE TABLE `crawls_website` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `domain` varchar(255) NOT NULL,
    `title` varchar(255) NULL,
    `description` longtext NULL,
    `homepage` varchar(200) NULL,
    `user_id` integer NOT NULL
);

-- Add field website to webpage
ALTER TABLE `crawls_webpage`
ADD COLUMN `website_id` integer NOT NULL,
ADD CONSTRAINT `crawls_webpage_website_id_5dec4ee6_fk_crawls_website_id` FOREIGN KEY (`website_id`) REFERENCES `crawls_website` (`id`);

-- Create model CrawlTask
CREATE TABLE `crawls_crawltask` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `status` varchar(10) NOT NULL,
    `start_time` datetime(6) NOT NULL,
    `end_time` datetime(6) NULL,
    `error_msg` longtext NULL,
    `user_id` integer NOT NULL,
    `website_id` integer NOT NULL
);

-- Create model Image
CREATE TABLE `crawls_image` (
    `url_id` varchar(500) NOT NULL PRIMARY KEY,
    `description` varchar(255) NOT NULL,
    `resolution` varchar(50) NOT NULL,
    `webpage_id` integer NOT NULL
);

-- Alter unique_together for webpage (1 constraint(s))
ALTER TABLE `crawls_webpage`
ADD CONSTRAINT `crawls_webpage_url_website_id_d0261562_uniq` UNIQUE (`url`, `website_id`);

ALTER TABLE `crawls_content`
ADD CONSTRAINT `crawls_content_webpage_id_285fd3a8_fk_crawls_webpage_id` FOREIGN KEY (`webpage_id`) REFERENCES `crawls_webpage` (`id`);

CREATE INDEX `crawls_content_keywords_0d3b71de` ON `crawls_content` (`keywords`);

ALTER TABLE `crawls_website`
ADD CONSTRAINT `crawls_website_user_id_domain_73d622c4_uniq` UNIQUE (`user_id`, `domain`);

ALTER TABLE `crawls_website`
ADD CONSTRAINT `crawls_website_user_id_08f8d9b4_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

ALTER TABLE `crawls_crawltask`
ADD CONSTRAINT `crawls_crawltask_user_id_b4d5827d_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

ALTER TABLE `crawls_crawltask`
ADD CONSTRAINT `crawls_crawltask_website_id_3baa3555_fk_crawls_website_id` FOREIGN KEY (`website_id`) REFERENCES `crawls_website` (`id`);

ALTER TABLE `crawls_image`
ADD CONSTRAINT `crawls_image_url_id_9d23e96f_fk_crawls_da` FOREIGN KEY (`url_id`) REFERENCES `crawls_datasource` (`data_source_url`);

ALTER TABLE `crawls_image`
ADD CONSTRAINT `crawls_image_webpage_id_0557f0e0_fk_crawls_webpage_id` FOREIGN KEY (`webpage_id`) REFERENCES `crawls_webpage` (`id`);

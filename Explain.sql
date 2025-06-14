-- 以下内容是本项目数据库结构与实际操作的示意SQL语句，注意该文件只是用作本项目涉及的
-- 数据库操作概念展示，实际操作已经嵌入Python代码，所以本文件不是运行项目的必须文件。
CREATE DATABASE samp_db;-- 在这里变成你本机的数据库名称。
use samp_db;
------------------------------表的创建-----------------------------------------------
--
-- Create model DataSource
--
CREATE TABLE `crawls_datasource` (
    `data_source_url` varchar(500) NOT NULL PRIMARY KEY,
    `publisher` varchar(100) NOT NULL,
    `publish_time` datetime(6) NOT NULL
);
--
-- Create model Webpage
--
CREATE TABLE `crawls_webpage` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `url` varchar(500) NOT NULL UNIQUE,
    `crawl_time` datetime(6) NOT NULL
);
--
-- Create model Website
--
CREATE TABLE `crawls_website` (
    `domain` varchar(255) NOT NULL PRIMARY KEY,
    `company` varchar(100) NOT NULL,
    `contact` varchar(100) NOT NULL,
    `crawl_freq` varchar(10) NOT NULL,
    `crawl_status` varchar(10) NOT NULL
);
--
-- Create model Image
--
CREATE TABLE `crawls_image` (
    `image_url` varchar(500) NOT NULL PRIMARY KEY,
    `description` varchar(255) NOT NULL,
    `resolution` varchar(50) NOT NULL,
    `data_source_id` varchar(500) NOT NULL,
    `webpage_id` varchar(500) NOT NULL
);
--
-- Create model Content
--
CREATE TABLE `crawls_content` (
    `content_id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `text` longtext NOT NULL,
    `keywords` varchar(500) NOT NULL,
    `type` varchar(10) NOT NULL,
    `webpage_id` varchar(500) NOT NULL
);
--
-- Add field website to webpage
--
ALTER TABLE `crawls_webpage`
ADD COLUMN `website_id` varchar(255) NOT NULL,
ADD CONSTRAINT `crawls_webpage_website_id_5dec4ee6_fk_crawls_website_domain` FOREIGN KEY (`website_id`) REFERENCES `crawls_website` (`domain`);
--
-- Create model DataSourceContent
--
CREATE TABLE `crawls_datasourcecontent` (
    `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `content_id` integer NOT NULL,
    `data_source_id` varchar(500) NOT NULL
);

ALTER TABLE `crawls_image`
ADD CONSTRAINT `crawls_image_data_source_id_aaca37d7_fk_crawls_da` FOREIGN KEY (`data_source_id`) REFERENCES `crawls_datasource` (`data_source_url`);

ALTER TABLE `crawls_image`
ADD CONSTRAINT `crawls_image_webpage_id_0557f0e0_fk_crawls_webpage_url` FOREIGN KEY (`webpage_id`) REFERENCES `crawls_webpage` (`url`);

ALTER TABLE `crawls_content`
ADD CONSTRAINT `crawls_content_webpage_id_285fd3a8_fk_crawls_webpage_url` FOREIGN KEY (`webpage_id`) REFERENCES `crawls_webpage` (`url`);

ALTER TABLE `crawls_datasourcecontent`
ADD CONSTRAINT `crawls_datasourcecontent_data_source_id_content_id_fbcd1817_uniq` UNIQUE (
    `data_source_id`,
    `content_id`
);

ALTER TABLE `crawls_datasourcecontent`
ADD CONSTRAINT `crawls_datasourcecon_content_id_e0cbab3c_fk_crawls_co` FOREIGN KEY (`content_id`) REFERENCES `crawls_content` (`content_id`);

ALTER TABLE `crawls_datasourcecontent`
ADD CONSTRAINT `crawls_datasourcecon_data_source_id_366d0a9c_fk_crawls_da` FOREIGN KEY (`data_source_id`) REFERENCES `crawls_datasource` (`data_source_url`);
-----------------------------------删除数据----------------------------------
SET FOREIGN_KEY_CHECKS = 0;
truncate table crawls_content;
truncate table crawls_image;
truncate table crawls_datasource;
truncate table crawls_datasourcecontent;
truncate table crawls_webpage;
truncate table crawls_website;
SET FOREIGN_KEY_CHECKS = 1;

-- 删除网页相关内容
DELETE FROM crawls_content
WHERE
    webpage_id = 'https://example.com/page1';

-- 删除网页相关图片（图片通过 DataSource 关联）
DELETE FROM crawls_image
WHERE
    webpage_id = 'https://example.com/page1';

-- 最后删除网页本身
DELETE FROM crawls_webpage WHERE url = 'https://example.com/page1';

-- 删除某网站的所有内容（通过网页）
DELETE FROM crawls_content
WHERE
    webpage_id IN (
        SELECT url
        FROM crawls_webpage
        WHERE
            website_id = 'example.com'
    );

-- 删除图片
DELETE FROM crawls_image
WHERE
    webpage_id IN (
        SELECT url
        FROM crawls_webpage
        WHERE
            website_id = 'example.com'
    );

-- 删除网页
DELETE FROM crawls_webpage WHERE website_id = 'example.com';

-- 删除网站
DELETE FROM crawls_website WHERE domain = 'example.com';

-- 删除中间表中的内容-数据源关联
DELETE FROM crawls_datasourcecontent
WHERE
    data_source_id = 'https://data.example.com/json1';

-- 删除图片（如果有关联）
DELETE FROM crawls_image
WHERE
    url_id = 'https://data.example.com/json1';

-- 删除数据源本体
DELETE FROM crawls_datasource
WHERE
    data_source_url = 'https://data.example.com/json1';
-- 根据关键字删除内容
DELETE FROM crawls_content WHERE keywords LIKE '%示例关键字%';
-- 删除那些爬取失败的website
DELETE FROM crawls_website WHERE crawl_status = 'fail';

-----------------------------------插入数据-------------------------------------
INSERT INTO
    crawls_website (
        domain,
        company,
        contact,
        crawl_freq,
        crawl_status,
        err
    )
VALUES (
        'example.com',
        '示例公司',
        'contact@example.com',
        'daily',
        'complete',
        NULL
    );
INSERT INTO
    crawls_webpage (url, crawl_time, website_id)
VALUES (
        'https://example.com/page1',
        '2025-06-14 15:00:00',
        'example.com'
    );
INSERT INTO
    crawls_content (
        text,
        webpage_id,
        keywords,
        type
    )
VALUES (
        '欢迎访问本站主页。',
        'https://example.com/page1',
        '欢迎,主页',
        'text'
    );
INSERT INTO
    crawls_image (
        url_id,
        webpage_id,
        description,
        resolution
    )
VALUES (
        'https://example.com/img1.jpg',
        'https://example.com/page1',
        'logo图片',
        '1920x1080'
    );
INSERT INTO
    crawls_datasource (
        data_source_url,
        publisher,
        publish_time
    )
VALUES (
        'https://example.com/img1.jpg',
        '示例发布者',
        '2025-06-14 10:30:00'
    );
INSERT INTO
    crawls_datasourcecontent (data_source_id, content_id)
VALUES (
        'https://example.com/img1.jpg',
        1
    );
-----------------------------------修改数据-------------------------------------
UPDATE crawls_website
SET
    company = '新公司名称',
    contact = 'new_contact@example.com',
    crawl_status = 'crawling',
    err = '暂时连接失败'
WHERE
    domain = 'example.com';
UPDATE crawls_webpage
SET
    crawl_time = '2025-06-14 18:00:00'
WHERE
    url = 'https://example.com/page1';
UPDATE crawls_content
SET
    keywords = '欢迎,主页,示例',
    type = 'link'
WHERE
    content_id = 1;
UPDATE crawls_image
SET
    description = '网站主图',
    resolution = '1280x720'
WHERE
    url_id = 'https://example.com/img1.jpg';
UPDATE crawls_datasource
SET
    publisher = '新发布者',
    publish_time = '2025-06-14 12:00:00'
WHERE
    data_source_url = 'https://example.com/img1.jpg';
-- DataDourceContent是联合主键所以得先删后加
-- 1. 先删除旧的
DELETE FROM crawls_datasourcecontent
WHERE
    data_source_id = 'https://example.com/img1.jpg'
    AND content_id = 1;
-- 2. 插入新的
INSERT INTO
    crawls_datasourcecontent (data_source_id, content_id)
VALUES (
        'https://example.com/img2.jpg',
        1
    );
-----------------------------------查找数据-------------------------------------
-- main_view
SELECT COUNT(*) FROM crawls_website;

SELECT COUNT(*) FROM crawls_webpage;

SELECT COUNT(*) FROM crawls_content;

SELECT w.*
FROM
    crawls_webpage w
    INNER JOIN crawls_website s ON w.website_id = s.domain
ORDER BY w.crawl_time DESC
LIMIT 5;

-- search_content_view
SELECT *
FROM
    crawls_content c
    INNER JOIN crawls_webpage w ON c.webpage_id = w.url
WHERE
    c.keywords ILIKE '%<query>%';

-- recent_websites
SELECT *
FROM crawls_website
WHERE
    crawl_status = 'complete'
ORDER BY domain DESC
LIMIT 10;

-- recent_websites
SELECT *
FROM crawls_website
WHERE
    crawl_status = 'complete'
ORDER BY domain DESC
LIMIT 10;

-- website_webpages_view
SELECT *
FROM crawls_webpage
WHERE
    website_id = '<domain>'
ORDER BY crawl_time DESC;

-- webpage_images_view
SELECT * FROM crawls_image WHERE webpage_id = '<url>';

--webpage_content_view
SELECT * FROM crawls_content WHERE webpage_id = '<url>';
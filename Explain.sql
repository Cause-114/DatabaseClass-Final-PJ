-- 以下内容是本项目数据库结构与实际操作的示意SQL语句，注意该文件只是用作本项目涉及的
-- 数据库操作概念展示，实际操作已经嵌入Python代码，所以本文件不是运行项目的必须文件。
CREATE DATABASE samp_db;
use samp_db;-- 在这里变成你本机的数据库名称。
------------------------------ Create core tables --------------------------------

-- Create model DataSource
CREATE TABLE `crawls_datasource` (
    `data_source_url` varchar(500) NOT NULL PRIMARY KEY,
    `publisher` varchar(100) NOT NULL,
    `publish_time` datetime(6) NOT NULL
);

-- Create model Website
CREATE TABLE `crawls_website` (
    `domain` varchar(255) NOT NULL PRIMARY KEY,
    `company` varchar(100) NOT NULL,
    `contact` varchar(100) NOT NULL,
    `crawl_freq` varchar(10) NOT NULL,
    `crawl_status` varchar(10) NOT NULL
);

-- Create model CrawlTask
CREATE TABLE `crawls_crawltask` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `task_time` datetime(6) NOT NULL,
    `status` varchar(10) NOT NULL,
    `website_id` varchar(255) NOT NULL,
    CONSTRAINT `crawls_crawltask_website_id_fk` FOREIGN KEY (`website_id`) REFERENCES `crawls_website` (`domain`)
);

-- Create model Webpage
CREATE TABLE `crawls_webpage` (
    `url` varchar(500) NOT NULL PRIMARY KEY,
    `crawl_time` datetime(6) NOT NULL,
    `website_id` varchar(255) NOT NULL,
    `crawltask_id` integer NOT NULL,
    CONSTRAINT `crawls_webpage_website_id_fk` FOREIGN KEY (`website_id`) REFERENCES `crawls_website` (`domain`),
    CONSTRAINT `crawls_webpage_crawltask_id_fk` FOREIGN KEY (`crawltask_id`) REFERENCES `crawls_crawltask` (`id`)
);

-- Create model Image
CREATE TABLE `crawls_image` (
    `image_url` varchar(500) NOT NULL PRIMARY KEY,
    `description` varchar(255) NOT NULL,
    `resolution` varchar(50) NOT NULL,
    `data_source_id` varchar(500) NOT NULL,
    `webpage_id` varchar(500) NOT NULL,
    CONSTRAINT `crawls_image_data_source_fk` FOREIGN KEY (`data_source_id`) REFERENCES `crawls_datasource` (`data_source_url`),
    CONSTRAINT `crawls_image_webpage_fk` FOREIGN KEY (`webpage_id`) REFERENCES `crawls_webpage` (`url`)
);

-- Create model Content
CREATE TABLE `crawls_content` (
    `content_id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `text` longtext NOT NULL,
    `keywords` varchar(500) NOT NULL,
    `type` varchar(10) NOT NULL,
    `webpage_id` varchar(500) NOT NULL,
    CONSTRAINT `crawls_content_webpage_fk` FOREIGN KEY (`webpage_id`) REFERENCES `crawls_webpage` (`url`)
);

-- Create model DataSourceContent (中间表)
CREATE TABLE `crawls_datasourcecontent` (
    `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `content_id` integer NOT NULL,
    `data_source_id` varchar(500) NOT NULL,
    CONSTRAINT `datasource_content_unique` UNIQUE (
        `data_source_id`,
        `content_id`
    ),
    CONSTRAINT `crawls_datasourcecontent_content_fk` FOREIGN KEY (`content_id`) REFERENCES `crawls_content` (`content_id`),
    CONSTRAINT `crawls_datasourcecontent_datasource_fk` FOREIGN KEY (`data_source_id`) REFERENCES `crawls_datasource` (`data_source_url`)
);
-----------------------------------删除数据----------------------------------
SET FOREIGN_KEY_CHECKS = 0;
truncate table crawls_content;
TRUNCATE TABLE crawls_crawltask;
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
-- 插入网站
INSERT INTO
    crawls_website (
        domain,
        company,
        contact,
        crawl_freq,
        crawl_status
    )
VALUES (
        'example.com',
        '示例公司',
        'contact@example.com',
        'daily',
        'complete'
    );

-- 插入爬取任务（与网站绑定）
INSERT INTO
    crawls_crawltask (task_time, status, website_id)
VALUES (
        '2025-06-14 14:30:00',
        'finished',
        'example.com'
    );

-- 假设刚刚插入的任务 id = 1（你可以用 SELECT LAST_INSERT_ID() 获取）

-- 插入网页（关联网站 & 任务）
INSERT INTO
    crawls_webpage (
        url,
        crawl_time,
        website_id,
        crawltask_id
    )
VALUES (
        'https://example.com/page1',
        '2025-06-14 15:00:00',
        'example.com',
        1
    );

-- 插入网页内容
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

-- 插入图片
INSERT INTO
    crawls_image (
        image_url,
        webpage_id,
        description,
        resolution,
        data_source_id
    )
VALUES (
        'https://example.com/img1.jpg',
        'https://example.com/page1',
        'logo图片',
        '1920x1080',
        'https://example.com/img1.jpg'
    );

-- 插入数据源
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

-- 插入数据源与内容的关联
INSERT INTO
    crawls_datasourcecontent (data_source_id, content_id)
VALUES (
        'https://example.com/img1.jpg',
        1
    );
-----------------------------------修改数据-------------------------------------
-- 修改网站信息
UPDATE crawls_website
SET
    company = '新公司名称',
    contact = 'new_contact@example.com',
    crawl_status = 'crawling'
WHERE
    domain = 'example.com';

-- 修改网页时间
UPDATE crawls_webpage
SET
    crawl_time = '2025-06-14 18:00:00'
WHERE
    url = 'https://example.com/page1';

-- 修改网页内容
UPDATE crawls_content
SET
    keywords = '欢迎,主页,示例',
    type = 'link'
WHERE
    content_id = 1;

-- 修改图片
UPDATE crawls_image
SET
    description = '网站主图',
    resolution = '1280x720'
WHERE
    image_url = 'https://example.com/img1.jpg';

-- 修改数据源
UPDATE crawls_datasource
SET
    publisher = '新发布者',
    publish_time = '2025-06-14 12:00:00'
WHERE
    data_source_url = 'https://example.com/img1.jpg';

-- 删除原有数据源-内容关联
DELETE FROM crawls_datasourcecontent
WHERE
    data_source_id = 'https://example.com/img1.jpg'
    AND content_id = 1;

-- 添加新的数据源-内容关联（假设换成 img2.jpg）
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
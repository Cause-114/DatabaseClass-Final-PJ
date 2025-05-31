-- 以下内容是本项目数据库结构的示意
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
    `url` varchar(500) NOT NULL PRIMARY KEY,
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
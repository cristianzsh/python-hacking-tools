from BeautifulSoup import BeautifulSoup
import re
import requests
import urlparse

class Scanner:
    def __init__(self, url, ignore):
        self.session = requests.Session()
        self.target = url
        self.target_links = []
        self.ignore = ignore
        
    def extract_links(self, url):
        response = self.session.get(url)
        return re.findall("(?:href=\")(.*?)\"", response.content)
    
    def crawl(self, url = None):
        if url == None:
            url = self.target

        links = self.extract_links(url)
        for link in links:
            link = urlparse.urljoin(url, link)
            
            if "#" in link:
                link = link.split("#")[0]
                
            if self.target in link and link not in self.target_links and link not in self.ignore:
                self.target_links.append(link)
                print(link)
                self.crawl(link)

    def extract_forms(self, url):
        response = self.session.get(url)
        parsed_html = BeautifulSoup(response.content)
        return parsed_html.findAll("form")

    def submit_form(self, form, value, url):
        action = form.get("action")
        post_url = urlparse.urljoin(url, action)
        method = form.get("method")

        inputs_list = form.findAll("input")
        post_data = {}
        for input in inputs_list:
            input_name = input.get("name")
            input_type = input.get("type")
            input_value = input.get("value")

            if input_type == "text":
                input_value = value

            post_data[input_name] = input_value

        if method == "post":
            return self.session.post(post_url, data = post_data)

        return self.session.get(post_url, params = post_data)

    def run_scanner(self):
        for link in self.target_links:
            forms = self.extract_forms(link)
            for form in forms:
                print("\033[94m[+]\033[0m Testing form in " + link)
                is_vulnerable_to_xss = self.test_xss_in_form(form, link)

                if is_vulnerable_to_xss:
                    print("\033[92m[***]\033[0m XSS discovered in " + link + " in the following form")
                    print(form)

            if "=" in link:
                print("\033[94m[+]\033[0m Testing " + link)
                is_vulnerable_to_xss = self.test_xss_in_link(link)
                if is_vulnerable_to_xss:
                    print("\033[92m[***]\033[0m Discovered XSS in " + link)

    def test_xss_in_form(self, form, url):
        xss_test_script = "<scriPt>alert('test')</scripT>"
        response = self.submit_form(form, xss_test_script, url)

        return xss_test_script in response.content

    def test_xss_in_link(self, url):
        xss_test_script = "<scriPt>alert('test')</scripT>"
        url = url.replace("=",  "=" + xss_test_script)
        response = self.session.get(url)

        return xss_test_script in response.content

if __name__ == "__main__":
    target = "http://10.0.2.5/dvwa/"
    ignore = ["http://10.0.2.5/dvwa/logout.php"]
    data_dict = {"username" : "admin", "password" : "password", "Login" : "submit"}

    scanner = Scanner(target, ignore)
    scanner.session.post("http://10.0.2.5/dvwa/login.php", data = data_dict)
    scanner.crawl()
    scanner.run_scanner()

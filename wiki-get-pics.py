try:
    import wikipedia
    import os, sys, time, requests, urllib.parse, tkinter
    from urllib.parse import parse_qs
    from pathlib import Path
    from typing import Dict, Tuple, Any

    #-------------------------------- init funcs

    class MyAppException(Exception): ...
    class WrongWikiURl(MyAppException): ...
    class OutputFolderExists(MyAppException): ...
    class CouldntGetPageTitle(MyAppException): ...
    class PageNotFound(MyAppException): ...
    class URLDoesntExist(MyAppException): ...


    def _return_error_text():
        '''
        returns error text in this format:\n
            `error_type:error_type{SEP}error_text:error_text{SEP}file:file{SEP}line:line`
        '''
        SEP = ' |SEP| '
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        return f'error_type:{exc_type.__name__}{SEP}error_text:{str(exc_obj)}{SEP}file:{fname}{SEP}line:{exc_tb.tb_lineno}'


    def escape_folder(given_name: str,
                    esc_kwargs: Dict[str, str] = {}):
        '''escape wrong folder name'''
        esc = {
            '\\' : '.',
            '/' : '.',
            ':' : '.',
            '*' : '#',
            '?' : '.',
            '"' : '\'',
            '<' : '{',
            '>' : '}',
            '|' : '^',
        }
        for key, val in esc_kwargs.items():
            esc[key] = val
        for key, val in esc.items():
            given_name = given_name.replace(key, val)
        return given_name

    #-------------------------------- init vars

    log_file = str(Path(os.getcwd()) / f'log-{time.time()}.txt')
    open(log_file, 'w', encoding='utf-8').close()
    
    output_folder = str(Path(os.getcwd()) / 'output')
    if os.path.isdir(output_folder):
        if len(os.listdir(output_folder)) != 0:
            raise OutputFolderExists
    else:
        os.mkdir(output_folder)

    #-------------------------------- main part

    def main(page_url):
        print('checking url...')
        if 'wikipedia.org' not in page_url or ('https://' not in page_url and 'http://' not in page_url):
            raise WrongWikiURl
        if not 200 <= requests.head(page_url).status_code < 300:
            raise URLDoesntExist
        print('url is valid!')
        
        page_title = urllib.parse.urlparse(page_url).path.rsplit('/', 1)[-1].strip()
        if page_title == '':
            raise CouldntGetPageTitle
        
        print('getting page... ', end='', flush=True)
        try:
            wiki = wikipedia.WikipediaPage(title=page_title)
            images = wiki.images
        except wikipedia.PageError:
            print()
            raise PageNotFound(f'https://en.wikipedia.org/wiki/{page_title}')
        print('found! download started... (check `output` folder)')
        
        
        for url in images:
            name = escape_folder(url.rsplit('/', 1)[-1])
            path = f'output/{name}'
            
            seconds = 1
            try:
                
                size = requests.head(
                    url,
                    allow_redirects=True,
                    headers={'User-Agent': 'CoolTool/0.0 (hamid80zamanian@gmail.com) generic-library/0.0'},
                ).headers.get('Content-Length')
                if size:
                    size = f'{int(size) / 1024 / 1024:.2f}M'
                else:
                    size = 'SIZE_NOT_FOUND'
                print(f'downloading {name} ({size})... ', end='', flush=True)
                
                r = requests.get(
                    url,
                    allow_redirects=True,
                    headers={'User-Agent': 'CoolTool/0.0 (hamid80zamanian@gmail.com) generic-library/0.0'},
                )
                if not 200 <= r.status_code < 300:
                    try:
                        error_text = f'couldnt download {url} | reason: {r.reason}'
                        print(error_text)
                        with open(log_file, 'a', encoding='utf-8') as f:
                            f.write(error_text)
                    except:
                        pass
                    continue
                seconds += 2
                with open(path, 'wb') as f:
                    f.write(r.content)
                print(f'done')
            
            except Exception as e:
                try:
                    error_text = f'couldnt process {url} | reason: {e}'
                    print(error_text)
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(error_text)
                except:
                    pass
            time.sleep(seconds)

    #-------------------------------- final part

    # https://en.wikipedia.org/wiki/List_of_paintings_by_J._M._W._Turner
    url = input('enter url: ')
    try:
        main(url)
    except OutputFolderExists:
        print(f'folder {output_folder} exists. delete it before using the bot')
    except WrongWikiURl:
        print(f'Wrong url. Your url must have `wikipedia.org` in it and start with `http://` or `https://`')
    except URLDoesntExist:
        print(f'your url doesnt exist: {url}')
    except CouldntGetPageTitle:
        print(f'The url you entered is not valid. couldnt find the page title')
    except PageNotFound as e:
        print(f'Coulnt find your page: {e}')
    except Exception:
        print(f'[ ERROR ] {_return_error_text()}')

    if open(log_file, encoding='utf-8').read().strip() == '':
        os.remove(log_file)
except Exception as e:
    try:
        print(f'[ ERROR ] {_return_error_text()}')
    except:
        print(f'[ ERROR ] {e}')
input('press enter to exit...')

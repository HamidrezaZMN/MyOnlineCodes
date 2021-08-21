try:
    import wikipedia
    import os, sys, time, requests, urllib.parse, tkinter, colorama
    from colorama import Fore, Style
    from tqdm import tqdm
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

    colorama.init()
    
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
        print('checking url... ', end='', flush=True)
        if 'wikipedia.org' not in page_url or ('https://' not in page_url and 'http://' not in page_url):
            raise WrongWikiURl
        if not 200 <= requests.head(page_url).status_code < 300:
            raise URLDoesntExist
        print(Fore.LIGHTGREEN_EX + 'valid!' + Style.RESET_ALL)
        
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
        print(Fore.LIGHTGREEN_EX + 'found!' + Style.RESET_ALL)
        
        if len(images) == 0:
            print(Fore.LIGHTYELLOW_EX + 'no images found on this page' + Style.RESET_ALL)
        
        else:
            print(Fore.LIGHTYELLOW_EX + f'downloading {len(images)} started... (check `output` folder)' + Style.RESET_ALL)
            for image_idx, url in enumerate(images):
                name = escape_folder(url.rsplit('/', 1)[-1])
                path = f'output/{name}'
                
                seconds = 1
                try:
                    
                    r = requests.get(
                        url,
                        allow_redirects=True, stream=True,
                        headers={'User-Agent': 'CoolTool/0.0 (hamid80zamanian@gmail.com) generic-library/0.0'},
                    )
                    if not 200 <= r.status_code < 300:
                        try:
                            print(f'{Fore.LIGHTMAGENTA_EX}couldnt download{Style.RESET_ALL} {url} | reason: {r.reason}')
                            with open(log_file, 'a', encoding='utf-8') as f:
                                f.write(f'couldnt download {url} | reason: {r.reason}')
                        except:
                            pass
                        continue
                    seconds += 2
                    total_size_in_bytes= int(r.headers.get('content-length', 0))
                    print(f'downloading {image_idx+1}- {name} ({total_size_in_bytes/1024/1024:.2f}M)... ')
                    block_size = 1024 #1 Kibibyte
                    progress_bar = tqdm(
                        total=total_size_in_bytes,
                        unit='iB',
                        unit_scale=True,
                        ncols=80,
                        bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{remaining}]')
                    with open(path, 'wb') as f:
                        for data in r.iter_content(block_size):
                            progress_bar.update(len(data))
                            f.write(data)
                    progress_bar.close()
                    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                        try:
                            print(f'{Fore.LIGHTMAGENTA_EX}couldnt download{Style.RESET_ALL} {url} | reason: {e}')
                            with open(log_file, 'a', encoding='utf-8') as f:
                                f.write(f'couldnt process {url} | reason: {e}')
                        except:
                            pass
                    print(Fore.LIGHTGREEN_EX + 'done' + Style.RESET_ALL)
                
                except Exception as e:
                    try:
                        print(f'{Fore.LIGHTMAGENTA_EX}couldnt download{Style.RESET_ALL} {url} | reason: {e}')
                        with open(log_file, 'a', encoding='utf-8') as f:
                            f.write(f'couldnt process {url} | reason: {e}')
                    except:
                        pass
                time.sleep(seconds)

    #-------------------------------- final part

    # https://en.wikipedia.org/wiki/List_of_paintings_by_J._M._W._Turner
    url = input('enter url: ')
    try:
        main(url)
    except WrongWikiURl:
        print(f'{Fore.LIGHTMAGENTA_EX}Wrong url{Style.RESET_ALL}. Your url must have `wikipedia.org` in it and start with `http://` or `https://`')
    except URLDoesntExist:
        print(f'{Fore.LIGHTMAGENTA_EX}your url doesnt exist{Style.RESET_ALL}: {url}')
    except CouldntGetPageTitle:
        print(f'{Fore.LIGHTMAGENTA_EX}The url you entered is not valid{Style.RESET_ALL}. couldnt find the page title')
    except PageNotFound as e:
        print(f'{Fore.LIGHTMAGENTA_EX}Coulnt find your page{Style.RESET_ALL}: {e}')
    except Exception:
        print(f'{Fore.LIGHTMAGENTA_EX}[ ERROR ]{Style.RESET_ALL} {_return_error_text()}')

    if open(log_file, encoding='utf-8').read().strip() == '':
        os.remove(log_file)

except OutputFolderExists:
    print(f'folder {output_folder} exists. delete or empty it before using the bot')
except Exception as e:
    try:
        print(f'[ ERROR ] {_return_error_text()}')
    except:
        print(f'[ ERROR ] {e}')
input('press enter to exit...')

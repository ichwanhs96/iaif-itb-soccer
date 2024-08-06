import os.path
import requests
import json
from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

PAGE_ID = 390170094177561 # IAIF facebook page ID https://www.facebook.com/profile.php?id=61563763236258

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]

def main():
  """Shows basic usage of the Drive v3 API.
  Prints the names and ids of the first 10 files the user has access to.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("drive", "v3", credentials=creds)

    # Call the Drive v3 API
    results = (
        service.files()
        .list(pageSize=10, fields="nextPageToken, files(id, name)")
        .execute()
    )
    items = results.get("files", [])

    if not items:
      print("No files found.")
      return
    print("Files:")
    for item in items:
      print(f"{item['name']} ({item['id']})")
  except HttpError as error:
    # TODO(developer) - Handle errors from drive API.
    print(f"An error occurred: {error}")

def post_test_message_to_facebook() -> None:
  msg = 'Hello 👋!'
  post_url = 'https://graph.facebook.com/v20.0/{}/feed'.format(PAGE_ID)
  payload = {
    'message': msg,
    'access_token': os.getenv('facebook_page_access_token')
  }
  r = requests.post(post_url, data=payload)
  print(r.text)

def upload_video_to_facebook(video_path: str):
  app_id = "412160031847038"

  # Get file details
  file_name = os.path.basename(video_path)
  file_size = os.path.getsize(video_path)
  file_type = "video/mp4"

  # Construct the URL
  url = f"https://graph.facebook.com/v20.0/{app_id}/uploads"

  # Set up the parameters
  params = {
      "file_name": file_name,
      "file_length": file_size,
      "file_type": file_type,
      "access_token": os.getenv('facebook_user_access_token')
  }

  # Make the POST request
  response = requests.post(url, params=params)

  # Check the response
  if response.status_code == 200:
      print("Upload request successful")
      upload_session_id = response.json().get('id')
      upload_response = upload_video_file_to_facebook(video_path, upload_session_id)
      post_video_to_facebook_page(PAGE_ID, upload_response.get('h'), 'Test Video', 'This is a test video! 🚀')
      print("Video published to IAIF page!")

  else:
      print(f"Upload request failed with status code: {response.status_code}")
      print(response.text)
      
def upload_video_file_to_facebook(video_path: str, upload_session_id: str) -> dict:
    upload_url = f"https://graph.facebook.com/v20.0/{upload_session_id}"
    
    # Prepare headers
    headers = {
        "Authorization": f"OAuth {os.getenv('facebook_user_access_token')}",
        "file_offset": "0"
    }
    
    # Open and read the video file
    with open(video_path, 'rb') as video_file:
        video_data = video_file.read()
    
    # Make the POST request to upload the video
    upload_response = requests.post(upload_url, headers=headers, data=video_data)
    
    if upload_response.status_code == 200:
        print("Video upload successful")
        print(upload_response.text)
        return upload_response.json()
    else:
        print(f"Video upload failed with status code: {upload_response.status_code}")
        print(upload_response.text)

def post_video_to_facebook_page(page_id: str, video_file_handle: str, title: str, description: str) -> None:
    url = f"https://graph-video.facebook.com/v20.0/{page_id}/videos"
    
    payload = {
        'access_token': os.getenv('facebook_page_access_token'),
        'title': title,
        'description': description,
        'fbuploader_video_file_chunk': video_file_handle
    }
    
    response = requests.post(url, data=payload)
    
    if response.status_code == 200:
        print("Video posted successfully")
        print(response.json())
    else:
        print(f"Failed to post video. Status code: {response.status_code}")
        print(response.text)

def upload_unpublished_photo_to_facebook(photo_path: str) -> str:
  url = "https://graph.facebook.com/{}/photos".format(PAGE_ID)
    
  with open(photo_path, 'rb') as photo_file:
      files = {
          'source': ('photo.jpg', photo_file, 'image/jpeg')
      }
      
      payload = {
          "published": "false",
          "access_token": os.getenv('facebook_page_access_token')
      }
      
      response = requests.post(url, files=files, data=payload)
  
  if response.status_code == 200:
      print("Photo uploaded successfully")
      return response.json().get('id')
  else:
      print(f"Failed to upload photo. Status code: {response.status_code}")
      print(response.text)

def publish_photo_to_facebook_page(photo_ids: list[str]) -> None:
  url = f"https://graph.facebook.com/{PAGE_ID}/feed"

  payload = {
      "message": "Testing multi-photo post!",
      "access_token": os.getenv('facebook_page_access_token')
  }
  
  for index, photo_id in enumerate(photo_ids):
      payload[f"attached_media[{index}]"] = json.dumps({"media_fbid": photo_id})
  
  response = requests.post(url, data=payload)
  
  if response.status_code == 200:
      print("Multi-photo post published successfully")
      print(response.json())
  else:
      print(f"Failed to publish multi-photo post. Status code: {response.status_code}")
      print(response.text)

if __name__ == "__main__":
  load_dotenv()
  main()
  script_directory = os.path.dirname(os.path.abspath(__file__))

  ### TESTING SCENARIO ###

  ### to test uploading video to facebook
  # upload_video_to_facebook(f'{script_directory}/test-video.mp4')

  # vid_file_handle = "4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARaU-mcq3YjjGzzhLUWaq2d1xZJj8PLGGckUYewZqdRF6TSkjJSfe004lRjZuqqBMMKaC2wX0gBpy7g7achLlBasFfwowng5zo5V-Mt55NBkfQ:e:1723278838:412160031847038:100001281514250:ARaxAz7mg2tYBPO-gbw\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARaC40VA9Iyz3ibNWL7v7H9NO8OESNcMCLYWsmLy_ajukBFTbhNF4Qnv-a_j-94dTY4ASu5QHaS-LlCputtF6R6fEq9zoqbk-NcOaflLLeoLmg:e:1723278838:412160031847038:100001281514250:ARYm-uQsTGoBPvlPrXI\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARYiBuC41-Dva_yd5ggOjF_VW8fjTwONQOghXpwxrXQ65Q5m18ahZh-6VCKkJTketTnjA-lBCuEu6iA8MeUEuQGekl4njBKrO7AREUxItLnXDg:e:1723278838:412160031847038:100001281514250:ARYgIezkzMF7rvxIHC4\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARaaHEI-G0k_yjcMVmcpyA_wr_56fEtOu2iMoyRG0TaCs2rAOaSWx0O818WL0tuYoMawRjZJDW3NNQmxBssVsn4gXbe4YqDN5qsZgymzwkublw:e:1723278838:412160031847038:100001281514250:ARawYsObml1EfDQloGw\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARaChxZe1mAxDDt4Zk2ePMd1rQl0ZZ7TFjX4F_b2LhQYwbra3Fo3ESUCXMQc9OiAuzGN_FMtGlgQv8DRQCdvJyHbIUiaTWm6JPkg7xOnxelR1g:e:1723278839:412160031847038:100001281514250:ARYKMKwjkzeW2KvrbAc\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARbL_aNB8JC1QsJYjG8G6TRl-k9H4vKIHQWI66kqeEzsOh5C0ASFiNMHQ3CTRizYh4uDxom14hndyCE1sYwMttcwPRnO14n57WBX6MfDZdqSNA:e:1723278839:412160031847038:100001281514250:ARbmXeGWLSmIoXzLNQA\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARageemXra8elwAs0Oo_IUbiDDx_jmQUe3L7qBwlfHGDiV2Ieu1hmmpBCkCPF_HVrD2AOj0hNduxZKmsX5DqmE3kzwD8bezi1Sk7ibOMf_QfZQ:e:1723278840:412160031847038:100001281514250:ARY2TBxZf3qg0N6lUTE\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARYJ2VVbmmndMGVOG1gySSnKG07drm3v76s1Z0gHUtHb04nOqBEC-cqnXRXmiuWg-xceT0OqbMeguU7IJkRgIpU8xTMVKVNRCkDv0a-XBq0ixA:e:1723278840:412160031847038:100001281514250:ARa0vU7zMGbjDZf059s\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARZ10matJtVr-y3egqYUIhaysVXb2uyl3_R1tb7Uk5NLxoEnZ2gR40yJXQyUy1wSuTasFAWmtkZttmYsgCF4DlC6nx8DkocgU57ySDxE-XF45g:e:1723278840:412160031847038:100001281514250:ARbp0Ao7QtQym_n3ggs\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARZFjG5ezXDwG0nPGxESbtghMFp54LmZwjoS0Xb3bfcSweO81Pv5h5c5uRZnKWhxSGFrV4P5FvJtrL1m9HizNBs6VbymoQIckGbEtIaV98oFcA:e:1723278841:412160031847038:100001281514250:ARaphCbwgiL67eo9eBE\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARZLWEuG1RyOO1DbDd4pieO8k_w_GuhSFEaYLOYGRttuyypEDxG1BgDOBMi5vOBz55n8P1eMK-nXNHxU5ZoX5HR2RiwreqziO4Do_8GrBEncmQ:e:1723278841:412160031847038:100001281514250:ARbm6tYrFrp69fk0wHg\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARZ9I5A36bV4Shbth_kZlQf7OG-QnXwe1ld372Peo9BE_vdoGLJd9hXz_ofyvCNV7NbjEcT9qDoxHdpyhnR6mcxEuEiOzzFqJ2HtC0sZJJ2yFg:e:1723278842:412160031847038:100001281514250:ARbvrWoTHhxBqELzSTw\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARYOqsVMnhpoWZ3DR3qQ1ydwY6hdt7XzYZ2OfMlrpRw6ULkuupSYdhnVayfD8pJZmnJt7M3OD0Hf-lIT8J2Qztkft8J_2WNXmPROWatJ72Fcaw:e:1723278842:412160031847038:100001281514250:ARbg1lZQ4iQDHT76PZY\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARbfdhnFHv649MX4u8duIZ7LvPxeJctGSIfvZyiMu-NpFAefeRlMPm0ZXh63Rnk7wb-tIsOYq3fl4hDt_ZqJlnF3Tv4r-Y1YeSqzzYm8eRLMLA:e:1723278843:412160031847038:100001281514250:ARYYEeyZ8V-7gSBeiwg\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARbgl6WpEfHUO-xC7vdxzpXDXXdKVV85BY6eIW6TzjxvgcUDu6gcx4tae04G5ZY1-k5vM-_FAxOYxGCPVagPeYCqk8XLUfRozp4poKC771fK2A:e:1723278843:412160031847038:100001281514250:ARZdISPLrOQ_LQfZcAc\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARawbJiFjbcMFVQuPmrKCFqgmrstgfBlUtz_IuGDwFT5lVmH0uxT_x67vrXkE87NxhxBc8F9O6L1lo6FHtD_GEttGSfUugug4JmlLXAPvdI0cg:e:1723278844:412160031847038:100001281514250:ARZ8Bdb-WT61vt0WFf0\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARa3m0sfGxhnZvfSV8MXqbl_N2Ejc00vcX2Hfw8GipWRxEUmc1L3qb6OlZ5Vtg36IWb2FzwMv5ivBkhdSvBxeWFPbVunoyM_pg7qlxzlK2RsIA:e:1723278845:412160031847038:100001281514250:ARYy8Vd-C3s478wV_eY\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARb8DosXojIxDDvFAWAo1FqgO2JYkFQjdzNkRcgvSQ6y9lGFboG0jy9hjphQGri1E3TvnoG23GiqtwjCzT-qOzP6m9U0e6oIzLUcadx3cYauTQ:e:1723278845:412160031847038:100001281514250:ARbF8XU1ossF-mgOZ00\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARa3pi3GFQkzFlqOhIIh7zWx8VTZiEzRj6bWFFXwa-3fKjKWrsGcDyrYDEQzSUP46By1uxzbjzEHNE91b6WJpDOd-HeMAdKsj4LYFAG-qU988w:e:1723278845:412160031847038:100001281514250:ARYQge6-GN_uiga0l8I\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARaF7m0Ce4TkTu99t1H2vAqZ7xlLYe57ltpk1BKCPbTaKkJmPUoeq0BZuBGfS4mlGbyuaHourdsM2feQu81KY3ZtHY2MbnOaubmMB5AMg0vu9w:e:1723278846:412160031847038:100001281514250:ARbv5TmueMVyVGJDxaw\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARaF-S2AFoibsP__WwXGMROVPR4JekW_4qox61ua1F06AkgdssEeNN_XYtU3CZabl8PHgECq6lET0y-L_5beTSU1XGEfZC7Ef2k-JF8E6-wL-g:e:1723278846:412160031847038:100001281514250:ARZExe8aBXrv6heq0qg\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARZLCCWxPvU8dLqhOP062LMosWXWYXjNtPaV8l4-1m08PgnuDDUPpP2JLP7v0YotJjFRG-k4D2T8pmSa7cPxP-PIKmSsRdW5PRBSjeLPejfEnA:e:1723278847:412160031847038:100001281514250:ARa3yyW4McrtKUNfO88\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARaZQXbS36qo5qfmIS0fn207oEeNXUy4L65xzg4lDdhzGrFROtmLlSdN75zx0XVRZ_9zl4FivUUbdbJBCwpBZp2-uyqB4H3eJ-FruQWgs0DSGQ:e:1723278847:412160031847038:100001281514250:ARYQ4Nsjjulkh6D-91s\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARZhrxSI9AFCZaheNGMmo4ukwCa68vVaETsDy0QpwSj4tH7CP-XQPHjgWOaQQk_zg0WHQ_OKyP-e-zhkYwp2sMpRrxU4bnixWKRWZLC4FFS-5A:e:1723278848:412160031847038:100001281514250:ARZoLfQJAmoBK1arSYw\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARancWAR_Rl9P_xuaQtCVERgDW_DTgf4cMv7FO5Ct3sUav6KN6KYWKQj_x17R_ncOBrhLHT7ZRFoyh2ptEOT6G9gXIVWri0poNsKx-zKGsqP8A:e:1723278849:412160031847038:100001281514250:ARasj6z0z7hJpq1gg0A\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARYRkZL-L3rdIgKDS3fxCfwQtDGfSfG8EwozcD7ENNANdtEWJqwMy02OrRnh5e87DLq6BsH7OWdnmW2FI_R8MPo83Bd_L7MZWlYYjDbae61P7A:e:1723278849:412160031847038:100001281514250:ARbDJiwwW5HAaWaCqF0\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARZyyCt655-JjRFfZ9OdX9vKttoutP7pIVIkoJ0100gP0APBNIUiOIjMpFM9Z3fcoQ8k7k_WZRn5Xs8zbs9JftyC-FiJP4pg8OEwBsWWgY35Ug:e:1723278849:412160031847038:100001281514250:ARZdRSKVYmGLlaW25tg\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARa1RvC-aDVvJCVaHj2_GlfB2b8bKa0TmEOlmQNlLUVrfO570IpsThUDnPXquO9dkPFuTjgcMr4MmhPtPqx9s5kS2JS8ktCbStx5CadLckLUWg:e:1723278850:412160031847038:100001281514250:ARZwmkWBzW1sYbhubDw\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARayQZSUYomoaEWgy94lWtZBa9vVehB0PO5kasWRNgz-TZKMnw-kVt_hu4KBmB_aMXb7-Bm_3guTsgzyA3dsdfGlBHx6Mylm4L4KsJozUn0Srw:e:1723278850:412160031847038:100001281514250:ARa-QNxEQqoistxfX4k\n4:dGVzdC12aWRlby5tcDQ=:dmlkZW8vbXA0:ARbK-_X2vZlE64RdPy8gL-iod8_pABp10n4DBCoToLK4zQxB6FyckI1WdULLxLXgHs-0wrkH8Ik9hbnIWS6D681o58ATJMnoy0jFYfpiH9hDZQ:e:1723278851:412160031847038:100001281514250:ARa5pVEJ2qWzap975lc"
  # post_video_to_facebook_page(PAGE_ID, vid_file_handle, 'Test Video', 'This is a test video! 🚀')

  ### Video upload had unresolved bug stated in here https://developers.facebook.com/community/threads/821620743399346/

  ### to test uploading multiple photos to facebook
  # photo_id = upload_unpublished_photo_to_facebook(f'{script_directory}/test-photo.jpeg')
  # publish_photo_to_facebook_page(["122100817070458774"])
# MUSEED Backend API Specification

MUSEED 백엔드는 FastAPI로 구현된 RESTful API를 제공합니다.  
본 문서는 프론트엔드 연동 및 외부 시스템 통합을 위한 상세 API 명세서입니다.

- **Base URL:** (Local) `http://localhost:8000`
- **Auth:** JWT (Bearer Token)
- **Content-Type:** `application/json`

---

## 1. 인증 (Authentication)

### `POST /api/auth/signup`
신규 사용자 회원가입을 처리합니다.

**Request Body:**
```json
{
  "username": "jayyoon",
  "nickname": "Jay",
  "password": "securepassword123",
  "email": "jay@example.com"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "jayyoon",
  "nickname": "Jay",
  "email": "jay@example.com",
  "is_active": true
}
```

### `POST /api/auth/token`
사용자 로그인 및 JWT 액세스 토큰을 발급받습니다.

**Request Body (Form Data):**
*   `username`: 사용자 ID
*   `password`: 비밀번호

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 2. 사용자 관리 (User Management)

### `GET /api/users/search`
사용자 ID 또는 닉네임으로 사용자를 검색합니다.

**Query Params:**
*   `q`: 검색어 (예: "jay")
*   `skip`: (Optional) 건너뛸 개수 (기본 0)
*   `limit`: (Optional) 가져올 개수 (기본 10)

**Response:**
```json
[
  {
    "id": 1,
    "username": "jayyoon",
    "nickname": "Jay",
    "profile_image_key": "Electronic"
  },
  {
    "id": 5,
    "username": "jay_music",
    "nickname": "JayMusic",
    "profile_image_key": "Default"
  }
]
```

### `GET /api/users/recommendations`
청취 기록 임베딩 유사도를 기반으로 취향이 비슷한 사용자를 추천합니다.

**Response:**
```json
[
  {
    "id": 5,
    "username": "jazz_lover",
    "nickname": "JazzCat",
    "profile_image_key": "Jazz",
    "similarity": 0.85
  }
]
```

### `GET /api/users/feed`
팔로잉한 사용자들의 최근 활동(플레이리스트 생성, 좋아요 등) 피드를 조회합니다.

**Response:**
```json
[
  {
    "id": 101,
    "user": {
      "id": 2,
      "username": "music_fan",
      "nickname": "Fan",
      "profile_image_key": "Default"
    },
    "action_type": "create_playlist",
    "target_playlist": {
      "id": 15,
      "name": "Best of Jazz",
      "is_public": true,
      "likes_count": 3
    },
    "created_at": "2024-12-14T10:30:00"
  }
]
```

### `GET /api/users/{username}`
특정 사용자의 상세 프로필 정보를 조회합니다.

**Response:**
```json
{
  "id": 1,
  "username": "jayyoon",
  "nickname": "Jay",
  "email": "jay@example.com",
  "is_active": true,
  "profile_image_key": "Electronic",
  "is_followed_by_current_user": false,
  "followers_count": 12,
  "following_count": 5,
  "achievements": [
    {
      "id": "seed_planter",
      "name": "Seed Planter",
      "description": "Created your first playlist.",
      "icon": "🌱"
    }
  ],
  "playlists": [
    {
      "id": 10,
      "name": "Morning Vibes",
      "is_public": true,
      "created_at": "2024-12-14T09:00:00",
      "likes_count": 5,
      "liked_by_user": false
    }
  ],
  "liked_playlists": []
}
```

### `PUT /api/users/{username}`
사용자 프로필(닉네임, 이메일, 비밀번호)을 수정합니다. (본인만 가능)

**Request Body:**
```json
{
  "nickname": "NewJayName",
  "email": "new_email@example.com",
  "password": "newpassword123"  // Optional
}
```

**Response:** (수정된 사용자 정보)
```json
{
  "id": 1,
  "username": "jayyoon",
  "nickname": "NewJayName",
  "email": "new_email@example.com",
  "is_active": true,
  "profile_image_key": "Electronic",
  ...
}
```

### `GET /api/users/{username}/stats`
사용자의 활동 통계(현재는 가장 많이 들은 장르)를 반환합니다.

**Response:**
```json
{
  "top_genre": "Electronic"
}
```

### `GET /api/users/{username}/genre-stats`
사용자의 전체 청취 기록에 기반한 장르별 분포 데이터를 반환합니다.

**Response:**
```json
[
  { "genre": "Electronic", "count": 150 },
  { "genre": "Pop", "count": 80 },
  { "genre": "Rock", "count": 45 }
]
```

### `POST /api/users/{username}/follow`
해당 사용자를 팔로우합니다.

**Response:** (팔로우 후 갱신된 대상 사용자 정보)
```json
{
  "id": 2,
  "username": "target_user",
  "followers_count": 13,
  "is_followed_by_current_user": true,
  ...
}
```

### `DELETE /api/users/{username}/follow`
해당 사용자를 언팔로우합니다.

**Response:** (언팔로우 후 갱신된 대상 사용자 정보)
```json
{
  "id": 2,
  "username": "target_user",
  "followers_count": 12,
  "is_followed_by_current_user": false,
  ...
}
```

### `GET /api/users/{username}/followers`
해당 사용자를 팔로우하는 사용자 목록을 조회합니다.

**Response:**
```json
[
  {
    "id": 3,
    "username": "follower1",
    "nickname": "Fan1",
    "profile_image_key": "Pop"
  },
  ...
]
```

### `GET /api/users/{username}/following`
해당 사용자가 팔로우하는 사용자 목록을 조회합니다.

**Response:**
```json
[
  {
    "id": 5,
    "username": "artist_official",
    "nickname": "Artist",
    "profile_image_key": "Rock"
  },
  ...
]
```

### `GET /api/users/{username}/playlists`
사용자가 생성한 플레이리스트 목록을 조회합니다.

**Response:**
```json
[
  {
    "id": 10,
    "name": "My Creation",
    "is_public": true,
    "owner_id": 1,
    "created_at": "2024-12-01T10:00:00",
    "likes_count": 5,
    "liked_by_user": false
  }
]
```

### `GET /api/users/{username}/likes`
사용자가 좋아요를 누른 플레이리스트 목록을 조회합니다.

**Response:**
```json
[
  {
    "id": 20,
    "name": "Liked Playlist",
    "is_public": true,
    "owner_id": 5,
    "created_at": "2024-11-20T15:00:00",
    "likes_count": 100,
    "liked_by_user": true
  }
]
```

---

## 3. 플레이리스트 및 AI 생성 (Playlists & Generation)

### `POST /api/playlists` (AI Generation)
기존 트랙(Seed Track) ID를 기반으로 AI 플레이리스트 생성을 비동기 요청합니다.

**Request Body:**
```json
{
  "name": "My AI Playlist",
  "seed_track_id": 12345
}
```

**Response:**
```json
{
  "task_id": "c62a0c40-1234-5678-9abc-def012345678",
  "status": "processing",
  "message": "Playlist generation started in background."
}
```

### `POST /api/playlists/upload` (AI Generation)
사용자가 오디오 파일을 업로드하여 AI 플레이리스트 생성을 비동기 요청합니다.

**Request Body (Multipart/Form-Data):**
*   `name`: "My Uploaded Playlist" (Text)
*   `file`: (Binary Audio File)

**Response:**
```json
{
  "task_id": "d12b0c40-5678-9012-3abc-efg456789012"
}
```

### `GET /api/playlists/task/{task_id}`
AI 생성 작업의 상태를 확인합니다.

**Response (Processing):**
```json
{
  "task_id": "c62a0c40-...",
  "status": "PENDING",
  "result": null
}
```

**Response (Success):**
```json
{
  "task_id": "c62a0c40-...",
  "status": "SUCCESS",
  "result": { "playlist_id": 25 }
}
```

### `GET /api/playlists/discover`
탐색 페이지용 공개 플레이리스트 목록을 최신순으로 조회합니다.

**Response:**
```json
[
  {
    "id": 30,
    "name": "New Releases Mix",
    "is_public": true,
    "owner": { "id": 8, "username": "dj_cool", "nickname": "DJ Cool" },
    "likes_count": 2,
    "liked_by_user": false
  },
  ...
]
```

### `GET /api/playlists/trending`
최근 24시간 내 좋아요 급상승 등 알고리즘에 따른 트렌딩 플레이리스트를 조회합니다.

**Response:**
```json
[
  {
    "id": 15,
    "name": "Viral Hits",
    "is_public": true,
    "owner": { "id": 3, "username": "trend_setter", "nickname": "Trend" },
    "likes_count": 500,
    "liked_by_user": true
  },
  ...
]
```

### `GET /api/playlists/search`
플레이리스트 제목으로 검색합니다.

**Query Params:**
*   `q`: 검색어 (예: "workout")
*   `skip`: 0
*   `limit`: 10

**Response:**
```json
[
  {
    "id": 40,
    "name": "Workout Energy",
    "is_public": true,
    "owner": { "id": 12, "username": "gym_user", "nickname": "Gym" },
    "likes_count": 20,
    "liked_by_user": false
  }
]
```

### `GET /api/playlists/{playlist_id}`
플레이리스트의 상세 정보와 포함된 트랙 목록을 조회합니다.

**Response:**
```json
{
  "id": 25,
  "name": "My AI Playlist",
  "is_public": true,
  "owner_id": 1,
  "created_at": "2024-12-14T12:00:00",
  "owner": {
    "id": 1,
    "username": "jayyoon",
    "nickname": "Jay"
  },
  "tracks": [
    {
      "id": 1,
      "position": 0,
      "track": {
        "track_id": 12345,
        "title": "Seed Song",
        "artist_name": "Artist A",
        "duration": 240,
        "genre_toplevel": "Electronic",
        "audio_url": "/api/tracks/12345/stream"
      }
    },
    {
      "id": 2,
      "position": 1,
      "track": {
        "track_id": 67890,
        "title": "Similar Track",
        "artist_name": "Artist B",
        "duration": 210,
        "genre_toplevel": "Electronic",
        "audio_url": "/api/tracks/67890/stream"
      }
    }
  ],
  "likes_count": 0,
  "liked_by_user": false
}
```

### `PUT /api/playlists/{playlist_id}`
플레이리스트 정보(제목, 공개 여부)를 수정합니다. (소유자 전용)

**Request Body:**
```json
{
  "name": "Updated Playlist Name",
  "is_public": false
}
```

**Response:**
```json
{
  "id": 25,
  "name": "Updated Playlist Name",
  "is_public": false,
  ...
}
```

### `DELETE /api/playlists/{playlist_id}`
플레이리스트를 삭제합니다. (소유자 전용)

**Response:**
```json
{
  "message": "Playlist deleted successfully"
}
```

### `POST /api/playlists/{playlist_id}/like`
플레이리스트에 좋아요를 추가합니다.

**Response:**
```json
{
  "id": 25,
  "name": "My AI Playlist",
  "likes_count": 1,
  "liked_by_user": true,
  ...
}
```

### `DELETE /api/playlists/{playlist_id}/like`
플레이리스트 좋아요를 취소합니다.

**Response:**
```json
{
  "id": 25,
  "name": "My AI Playlist",
  "likes_count": 0,
  "liked_by_user": false,
  ...
}
```

### `POST /api/playlists/{playlist_id}/tracks/{track_id}`
플레이리스트에 특정 트랙을 추가합니다. (소유자 전용)

**Response:**
```json
{
  "message": "Track added to playlist"
}
```

### `DELETE /api/playlists/{playlist_id}/tracks/{track_id}`
플레이리스트에서 특정 트랙(해당 ID를 가진 모든 엔트리)을 제거합니다. (소유자 전용)

**Response:**
```json
{
  "message": "Track removed from playlist"
}
```

### `PUT /api/playlists/{playlist_id}/tracks/reorder`
플레이리스트 내 트랙 순서를 변경합니다. (소유자 전용)

**Request Body:**
```json
{
  "track_ids": [67890, 12345]  // 재정렬된 트랙 ID 리스트
}
```

**Response:**
```json
{
  "message": "Tracks reordered successfully"
}
```

### `DELETE /api/playlists/{playlist_id}/entries/{entry_id}`
플레이리스트 내 특정 위치(Entry ID)의 트랙을 제거합니다. (중복 곡 삭제 시 유용)

**Response:**
```json
{
  "message": "Playlist entry removed successfully"
}
```

---

## 4. 트랙 및 오디오 (Tracks & Audio)

### `GET /api/tracks/search`
FMA 및 Jamendo 데이터베이스에서 트랙을 검색합니다.

**Query Params:** `q=piano`, `limit=5`

**Response:**
```json
[
  {
    "track_id": 555,
    "title": "Piano Sonata",
    "artist_name": "Classic Artist",
    "duration": 300,
    "genre_toplevel": "Classical",
    "audio_url": "/api/tracks/555/stream"
  }
]
```

### `GET /api/tracks/{track_id}/stream`
해당 트랙의 오디오 파일을 스트리밍합니다.
*   **Header:** `Content-Type: audio/mpeg`

---

## 5. 청취 기록 (History)

### `POST /api/history/listen`
사용자가 곡을 재생했을 때 청취 기록을 저장합니다. (추천 시스템 및 통계용)

**Request Body:**
```json
{
  "track_id": 12345,
  "genre": "Electronic"
}
```

**Response:**
```json
{
  "id": 501,
  "user_id": 1,
  "track_id": 12345,
  "genre": "Electronic",
  "listened_at": "2024-12-14T12:05:00"
}
```

---

## 6. 시스템 상태 (System Status)

### `GET /api/status`
서버 헬스 체크용 엔드포인트입니다.
**Response:**
```json
{
  "status": "ok"
}
```

### `GET /api/stats`
서비스 전체 통계를 반환합니다 (총 유저 수, 트랙 수, 플레이리스트 수).
**Response:**
```json
{
  "tracks": 88224,
  "users": 150,
  "playlists": 450
}
```

'use client';

import { useState, useEffect } from 'react';

interface TeamMember {
  id: string;
  name: string;
  role: string;
  avatar: string;
  status: 'online' | 'offline' | 'busy';
  lastActive?: string;
}

interface Comment {
  id: string;
  author: TeamMember;
  content: string;
  timestamp: string;
  resolved: boolean;
}

interface Activity {
  id: string;
  user: TeamMember;
  action: string;
  target: string;
  timestamp: string;
}

export default function Collaboration() {
  const [teamMembers] = useState<TeamMember[]>([
    { id: '1', name: '김대표', role: 'CEO', avatar: '👨‍💼', status: 'online' },
    { id: '2', name: '이마케터', role: '마케팅팀장', avatar: '👩‍💻', status: 'online' },
    { id: '3', name: '박에디터', role: '콘텐츠 에디터', avatar: '✍️', status: 'busy' },
    { id: '4', name: '최개발', role: '개발자', avatar: '👨‍💻', status: 'offline', lastActive: '10분 전' }
  ]);

  const [selectedContent, setSelectedContent] = useState({
    title: 'AI 시대의 콘텐츠 마케팅 전략',
    status: 'review',
    assignee: teamMembers[2]
  });

  const [comments, setComments] = useState<Comment[]>([
    {
      id: '1',
      author: teamMembers[1],
      content: '도입부가 너무 길어요. 핵심을 먼저 제시하면 좋겠습니다.',
      timestamp: '10분 전',
      resolved: false
    },
    {
      id: '2',
      author: teamMembers[2],
      content: '수정했습니다! 확인 부탁드려요.',
      timestamp: '5분 전',
      resolved: false
    }
  ]);

  const [activities] = useState<Activity[]>([
    {
      id: '1',
      user: teamMembers[0],
      action: '승인함',
      target: '블로그 자동화의 미래',
      timestamp: '방금 전'
    },
    {
      id: '2',
      user: teamMembers[1],
      action: '댓글 추가',
      target: 'AI 시대의 콘텐츠 마케팅 전략',
      timestamp: '10분 전'
    },
    {
      id: '3',
      user: teamMembers[2],
      action: '수정함',
      target: 'SEO 최적화 가이드',
      timestamp: '1시간 전'
    }
  ]);

  const [newComment, setNewComment] = useState('');
  const [showNotification, setShowNotification] = useState(false);

  // 실시간 업데이트 시뮬레이션
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowNotification(true);
      setTimeout(() => setShowNotification(false), 3000);
    }, 5000);

    return () => clearTimeout(timer);
  }, []);

  const addComment = () => {
    if (!newComment.trim()) return;

    const comment: Comment = {
      id: Date.now().toString(),
      author: teamMembers[0], // 현재 사용자
      content: newComment,
      timestamp: '방금 전',
      resolved: false
    };

    setComments([...comments, comment]);
    setNewComment('');
  };

  const workflowStages = [
    { name: '초안', status: 'completed', icon: '📝' },
    { name: '검토', status: 'active', icon: '👀' },
    { name: '수정', status: 'pending', icon: '✏️' },
    { name: '승인', status: 'pending', icon: '✅' },
    { name: '발행', status: 'pending', icon: '🚀' }
  ];

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* 알림 */}
      {showNotification && (
        <div className="fixed top-20 right-6 bg-blue-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-slide-in">
          <div className="flex items-center gap-2">
            <span>🔔</span>
            <span>박에디터님이 콘텐츠를 수정했습니다</span>
          </div>
        </div>
      )}

      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">실시간 협업</h1>
        <p className="text-gray-600">팀원들과 함께 콘텐츠를 검토하고 개선하세요</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 메인 콘텐츠 영역 */}
        <div className="lg:col-span-2 space-y-6">
          {/* 워크플로우 상태 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">워크플로우 진행 상황</h2>
            <div className="flex items-center justify-between">
              {workflowStages.map((stage, index) => (
                <div key={index} className="flex-1 text-center">
                  <div className={`w-12 h-12 mx-auto rounded-full flex items-center justify-center text-xl mb-2 ${
                    stage.status === 'completed' ? 'bg-green-100 text-green-600' :
                    stage.status === 'active' ? 'bg-blue-100 text-blue-600' :
                    'bg-gray-100 text-gray-400'
                  }`}>
                    {stage.icon}
                  </div>
                  <p className={`text-sm font-medium ${
                    stage.status === 'active' ? 'text-blue-600' : 'text-gray-600'
                  }`}>
                    {stage.name}
                  </p>
                  {index < workflowStages.length - 1 && (
                    <div className={`absolute w-full h-1 top-6 ${
                      index < 2 ? 'bg-green-300' : 'bg-gray-300'
                    }`} style={{ left: '50%', width: '100%' }} />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* 콘텐츠 상세 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-xl font-semibold">{selectedContent.title}</h2>
                <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                  <span>담당자: {selectedContent.assignee.name}</span>
                  <span>상태: 검토 중</span>
                </div>
              </div>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                편집하기
              </button>
            </div>

            <div className="prose max-w-none">
              <p className="text-gray-700">
                인공지능 기술의 발전으로 콘텐츠 마케팅 환경이 빠르게 변화하고 있습니다. 
                이제는 단순히 콘텐츠를 생산하는 것을 넘어서, AI를 활용하여 더 효과적이고 
                개인화된 콘텐츠를 제공하는 것이 중요해졌습니다...
              </p>
            </div>
          </div>

          {/* 댓글 섹션 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">댓글 및 피드백</h3>
            
            <div className="space-y-4 mb-6">
              {comments.map((comment) => (
                <div key={comment.id} className={`flex gap-3 ${comment.resolved ? 'opacity-60' : ''}`}>
                  <div className="text-2xl">{comment.author.avatar}</div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium">{comment.author.name}</span>
                      <span className="text-sm text-gray-500">{comment.timestamp}</span>
                      {!comment.resolved && (
                        <button className="text-sm text-blue-600 hover:underline">
                          해결됨으로 표시
                        </button>
                      )}
                    </div>
                    <p className="text-gray-700">{comment.content}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addComment()}
                className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="댓글을 입력하세요..."
              />
              <button
                onClick={addComment}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                전송
              </button>
            </div>
          </div>
        </div>

        {/* 사이드바 */}
        <div className="space-y-6">
          {/* 팀 멤버 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">팀 멤버</h3>
            <div className="space-y-3">
              {teamMembers.map((member) => (
                <div key={member.id} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="text-2xl">{member.avatar}</div>
                    <div>
                      <p className="font-medium">{member.name}</p>
                      <p className="text-sm text-gray-600">{member.role}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${
                      member.status === 'online' ? 'bg-green-500' :
                      member.status === 'busy' ? 'bg-yellow-500' :
                      'bg-gray-400'
                    }`} />
                    {member.status === 'offline' && member.lastActive && (
                      <span className="text-xs text-gray-500">{member.lastActive}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 최근 활동 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">최근 활동</h3>
            <div className="space-y-3">
              {activities.map((activity) => (
                <div key={activity.id} className="flex items-start gap-3">
                  <div className="text-xl mt-1">{activity.user.avatar}</div>
                  <div className="flex-1">
                    <p className="text-sm">
                      <span className="font-medium">{activity.user.name}</span>님이{' '}
                      <span className="text-blue-600">{activity.target}</span>을(를){' '}
                      {activity.action}
                    </p>
                    <p className="text-xs text-gray-500">{activity.timestamp}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 빠른 작업 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">빠른 작업</h3>
            <div className="space-y-2">
              <button className="w-full text-left px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors">
                ✅ 승인하기
              </button>
              <button className="w-full text-left px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors">
                ↩️ 수정 요청
              </button>
              <button className="w-full text-left px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors">
                👥 담당자 변경
              </button>
              <button className="w-full text-left px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors">
                📅 일정 조정
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
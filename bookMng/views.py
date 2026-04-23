from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from django.contrib import messages
from django.db.models import Q

from .models import MainMenu, Book, MessageThread, PrivateMessage
from .forms import BookForm, RegisterForm


# ---------- INDEX ----------
def index(request):
    return render(request, 'bookMng/index.html', {
        'item_list': MainMenu.objects.order_by('menu_order')
    })


# ---------- POST BOOK ----------
def postbook(request):
    submitted = False

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            try:
                book.username = request.user
            except Exception:
                pass
            book.save()
            return HttpResponseRedirect('/postbook?submitted=True')
    else:
        form = BookForm()
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'bookMng/postbook.html', {
        'form': form,
        'item_list': MainMenu.objects.order_by('menu_order'),
        'submitted': submitted
    })


# ---------- DISPLAY ----------
def displaybooks(request):
    books = Book.objects.all()
    return render(request, 'bookMng/displaybooks.html', {
        'item_list': MainMenu.objects.order_by('menu_order'),
        'books': books
    })


# ---------- MY BOOKS ----------
def mybooks(request):
    books = Book.objects.filter(username=request.user)
    return render(request, 'bookMng/mybooks.html', {
        'item_list': MainMenu.objects.order_by('menu_order'),
        'books': books
    })


# ---------- DETAIL ----------
def book_detail(request, book_id):
    book = Book.objects.get(id=book_id)
    return render(request, 'bookMng/book_detail.html', {
        'item_list': MainMenu.objects.order_by('menu_order'),
        'book': book
    })


# ---------- DELETE ----------
def book_delete(request, book_id):
    book = Book.objects.get(id=book_id)
    book.delete()
    return render(request, 'bookMng/book_delete.html', {
        'item_list': MainMenu.objects.order_by('menu_order'),
    })


# ---------- REGISTER ----------
class Register(CreateView):
    template_name = 'registration/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('register-success')

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.success_url)


User = get_user_model()


# ---------- INBOX ----------
@login_required
@require_GET
def inbox(request):
    threads = (
        MessageThread.objects
        .filter(Q(user1=request.user) | Q(user2=request.user))
        .prefetch_related("messages", "user1", "user2")
        .order_by("-updated_at")
    )

    thread_data = []
    for thread in threads:
        thread_data.append({
            "thread": thread,
            "other_user": thread.other_user(request.user),
            "latest_message": thread.latest_message(),
            "unread_count": thread.unread_count_for(request.user),
        })

    return render(request, "bookMng/inbox.html", {
        "thread_data": thread_data
    })


# ---------- THREAD ----------
@login_required
@require_http_methods(["GET", "POST"])
def thread_detail(request, thread_id):
    thread = get_object_or_404(
        MessageThread.objects.select_related("user1", "user2"),
        pk=thread_id,
    )

    if not thread.has_participant(request.user):
        raise Http404("Message thread not found.")

    if request.method == "POST":
        body = request.POST.get("body", "").strip()

        if not body:
            messages.error(request, "Message body cannot be empty.")
            return redirect("thread_detail", thread_id=thread.id)

        recipient = thread.other_user(request.user)

        PrivateMessage.objects.create(
            thread=thread,
            sender=request.user,
            recipient=recipient,
            body=body,
        )

        thread.save(update_fields=["updated_at"])
        messages.success(request, "Message sent.")
        return redirect("thread_detail", thread_id=thread.id)

    thread_messages = thread.messages.select_related("sender", "recipient").all()

    unread_messages = thread_messages.filter(recipient=request.user, is_read=False)
    for msg in unread_messages:
        msg.mark_as_read()

    return render(request, "bookMng/thread.html", {
        "thread": thread,
        "other_user": thread.other_user(request.user),
        "thread_messages": thread_messages,
    })


# ---------- COMPOSE ----------
@login_required
@require_http_methods(["GET", "POST"])
def compose_message(request):
    user_id = request.GET.get("user_id") or request.POST.get("user_id")
    selected_user = None

    if user_id:
        selected_user = get_object_or_404(User, pk=user_id)
        if selected_user == request.user:
            messages.error(request, "You cannot send a message to yourself.")
            return redirect("inbox")

    available_users = User.objects.exclude(pk=request.user.pk).order_by("username")

    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        target_user_id = request.POST.get("user_id")

        if not target_user_id:
            messages.error(request, "Please choose a recipient.")
            return render(request, "bookMng/compose.html", {
                "available_users": available_users,
                "selected_user": selected_user,
            })

        recipient = get_object_or_404(User, pk=target_user_id)

        if not body:
            messages.error(request, "Message body cannot be empty.")
            return render(request, "bookMng/compose.html", {
                "available_users": available_users,
                "selected_user": recipient,
            })

        thread = MessageThread.get_or_create_thread(request.user, recipient)

        PrivateMessage.objects.create(
            thread=thread,
            sender=request.user,
            recipient=recipient,
            body=body,
        )

        thread.save(update_fields=["updated_at"])

        messages.success(request, f"Message sent to {recipient.username}.")
        return redirect("thread_detail", thread_id=thread.id)

    return render(request, "bookMng/compose.html", {
        "available_users": available_users,
        "selected_user": selected_user,
    })


# ---------- MARK READ ----------
@login_required
@require_POST
def mark_thread_read(request, thread_id):
    thread = get_object_or_404(MessageThread, pk=thread_id)

    if not thread.has_participant(request.user):
        raise Http404("Message thread not found.")

    unread_messages = thread.messages.filter(recipient=request.user, is_read=False)
    for msg in unread_messages:
        msg.mark_as_read()

    messages.success(request, "Thread marked as read.")
    return redirect("thread_detail", thread_id=thread.id)


# ---------- ABOUT ----------
def aboutus(request):
    return render(request, 'bookMng/aboutus.html', {
        'item_list': MainMenu.objects.order_by('menu_order')
    })


# ---------- SEARCH ----------
def searchbooks(request):
    query = request.GET.get('q', '')
    books = Book.objects.all()

    if query:
        books = Book.objects.filter(name__icontains=query)

    return render(request, 'bookMng/searchbooks.html', {
        'item_list': MainMenu.objects.order_by('menu_order'),
        'books': books,
        'query': query
    })


# ---------- CART ----------
@require_POST
def add_to_cart(request, book_id):
    cart = request.session.get('cart', {})

    book_id = str(book_id)
    if book_id in cart:
        cart[book_id] += 1
    else:
        cart[book_id] = 1

    request.session['cart'] = cart
    return redirect('searchbooks')


def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for book_id, quantity in cart.items():
        try:
            book = Book.objects.get(id=book_id)
            subtotal = book.price * quantity
            total += subtotal
            cart_items.append({
                'book': book,
                'quantity': quantity,
                'subtotal': subtotal,
            })
        except Book.DoesNotExist:
            pass

    return render(request, 'bookMng/cart.html', {
        'cart_items': cart_items,
        'total': total,
    })


def checkout_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for book_id, quantity in cart.items():
        try:
            book = Book.objects.get(id=book_id)
            subtotal = book.price * quantity
            total += subtotal
            cart_items.append({
                'book': book,
                'quantity': quantity,
                'subtotal': subtotal,
            })
        except Book.DoesNotExist:
            pass

    return render(request, 'bookMng/checkout.html', {
        'cart_items': cart_items,
        'total': total,
    })


@require_POST
def remove_from_cart(request, book_id):
    cart = request.session.get('cart', {})
    book_id = str(book_id)

    if book_id in cart:
        del cart[book_id]

    request.session['cart'] = cart
    return redirect('cart')


def policy_page(request, policy_type):
    item_list = MainMenu.objects.order_by('menu_order')

    policies = {
        'privacy': {
            'title': 'Privacy Policy',
            'content': """
    We want users to feel safe using Book System.

    We collect basic information such as username and account details to provide our services.
    Your information is used only for platform functionality, communication, and improving user experience.

    We do not sell, trade, or share your personal data with third parties.
    All data is handled securely and only accessed when necessary for system operations.

    Users are responsible for keeping their account credentials safe.
    Any suspicious activity should be reported immediately.

    By using Book System, you agree to this privacy policy and how your data is handled.
    """
        },

        'refund': {
            'title': 'Refund Policy',
            'content': """
    We want users to feel safe using Book System.

    If there is a problem with a purchase, refund requests should be made within 7 days.
    The item should match the description shown in the listing.
    If a seller provides incorrect or misleading information, the buyer may request a refund.
    Refund decisions are reviewed case by case.
    Book System may contact both buyer and seller before making a final decision.

    Refunds may not be guaranteed in all cases, especially if the issue is caused by misuse
    or failure to follow agreed transaction terms.
    """
        },

        'shipping': {
            'title': 'Shipping Policy',
            'content': """
    Books should be shipped within 3 business days after purchase unless another arrangement is agreed on.
    Sellers should package books carefully to prevent damage.
    Delivery times may vary depending on location and shipping method.
    Buyers should make sure their shipping information is correct before placing an order.
    Book System is not responsible for delays caused by carriers, weather, or incorrect addresses.

    Tracking information should be provided when available to ensure transparency between buyer and seller.
    """
        },

        'terms': {
            'title': 'Terms of Service',
            'content': """
    By using Book System, you agree to use the platform responsibly.
    Users must provide accurate information when posting books or creating accounts.
    Listings must not contain false, harmful, or illegal content.
    Users must treat other users respectfully in messages and transactions.
    Book System reserves the right to remove listings or suspend accounts that violate these rules.

    Repeated violations or abusive behavior may result in permanent account suspension.
    """
        }
    }

    policy = policies.get(policy_type)

    if not policy:
        raise Http404("Policy page not found.")

    return render(request, 'bookMng/policy.html', {
        'item_list': item_list,
        'title': policy['title'],
        'content': policy['content']
    })